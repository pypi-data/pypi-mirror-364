import importlib.util
from pathlib import Path

from mcp.client.streamable_http import RequestContext
from starlette.requests import Request

import openai
import lancedb
import json

from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field
from typing import Any, Optional, List, cast, Literal, Tuple
from openai.types.chat import ChatCompletionSystemMessageParam
from starlette.responses import JSONResponse

from mcp_server_twelve_data.common import get_tokens_from_rc, create_dummy_request_context


def get_md_response(
    client: openai.OpenAI,
    llm_model: str,
    query: str,
    result: BaseModel
) -> str:
    prompt = """
    You are a Markdown report generator.
    
    Your task is to generate a clear, well-structured and readable response in Markdown format based on:
    1. A user query
    2. A JSON object containing the data relevant to the query
    
    Instructions:
    - Do NOT include raw JSON.
    - Instead, extract relevant information and present it using Markdown structure: headings, bullet points, tables,
      bold/italic text, etc.
    - Be concise, accurate, and helpful.
    - If the data is insufficient to fully answer the query, say so clearly.
    
    Respond only with Markdown. Do not explain or include extra commentary outside of the Markdown response.
    """

    llm_response = client.chat.completions.create(
        model=llm_model,
        messages=[
            cast(ChatCompletionSystemMessageParam, {"role": "system", "content": prompt}),
            cast(ChatCompletionSystemMessageParam, {"role": "user", "content": f"User query:\n{query}"}),
            cast(ChatCompletionSystemMessageParam, {"role": "user", "content": f"Data:\n{result.model_dump_json()}"}),
        ],
        temperature=0,
    )

    return llm_response.choices[0].message.content.strip()


class ToolPlanMap:
    def __init__(self, df):
        self.df = df
        self.plan_to_int = {
            'basic': 0,
            'grow': 1,
            'pro': 2,
            'ultra': 3,
            'enterprise': 4,
        }

    def split(self, user_plan: Optional[str], tool_operation_ids: List[str]) -> Tuple[List[str], List[str]]:
        if user_plan is None:
            # if user plan param was not specified, then we have no restrictions for function calling
            return tool_operation_ids, []
        user_plan_key = user_plan.lower()
        user_plan_int = self.plan_to_int.get(user_plan_key)
        if user_plan_int is None:
            raise ValueError(f"Wrong user_plan: '{user_plan}'")

        tools_df = self.df[self.df["id"].isin(tool_operation_ids)]

        candidates = []
        premium_only_candidates = []

        for _, row in tools_df.iterrows():
            tool_id = row["id"]
            tool_plan_raw = row["x-starting-plan"]
            if tool_plan_raw is None:
                tool_plan_raw = 'basic'

            tool_plan_key = tool_plan_raw.lower()
            tool_plan_int = self.plan_to_int.get(tool_plan_key)
            if tool_plan_int is None:
                raise ValueError(f"Wrong tool_starting_plan: '{tool_plan_key}'")

            if user_plan_int >= tool_plan_int:
                candidates.append(tool_id)
            else:
                premium_only_candidates.append(tool_id)

        return candidates, premium_only_candidates


def register_u_tool(
    server: FastMCP,
    u_tool_open_ai_api_key: Optional[str],
    transport: Literal["stdio", "sse", "streamable-http"],
):
    # llm_model = "gpt-4o"         # Input $2.5,   Output $10
    # llm_model = "gpt-4-turbo"    # Input $10.00, Output $30
    llm_model = "gpt-4o-mini"    # Input $0.15,  Output $0.60
    # llm_model = "gpt-4.1-nano"     # Input $0.10,  Output $0.40

    EMBEDDING_MODEL = "text-embedding-3-large"
    spec = importlib.util.find_spec("mcp_server_twelve_data")
    MODULE_PATH = Path(spec.origin).resolve()
    PACKAGE_ROOT = MODULE_PATH.parent  # src/mcp_server_twelve_data
    DB_PATH = str(PACKAGE_ROOT / "resources" / "endpoints.lancedb")
    TOP_N = 30

    class UToolResponse(BaseModel):
        """Response object returned by the u-tool."""

        top_candidates: Optional[List[str]] = Field(
            ..., description="List of tool operationIds considered by the vector search."
        )
        premium_only_candidates: Optional[List[str]] = Field(
            None, description="Relevant tool IDs available only in higher-tier plans"
        )
        selected_tool: Optional[str] = Field(
            None, description="Name (operationId) of the tool selected by the LLM."
        )
        param: Optional[dict] = Field(
            None, description="Parameters passed to the selected tool."
        )
        response: Optional[Any] = Field(
            None, description="Result returned by the selected tool."
        )
        error: Optional[str] = Field(
            None, description="Error message, if tool resolution or execution fails."
        )

    def constructor_for_utool(
        top_candidates=None,
        selected_tool=None,
        param=None,
        response=None,
        error=None,
        premium_only_candidates=None,
    ):
        return UToolResponse(
            top_candidates=top_candidates,
            selected_tool=selected_tool,
            param=param,
            response=response,
            error=error,
            premium_only_candidates=premium_only_candidates,
        )

    def build_openai_tools_subset(tool_list):
        def expand_parameters(params):
            if (
                "properties" in params and
                "params" in params["properties"] and
                "$ref" in params["properties"]["params"] and
                "$defs" in params
            ):
                ref_path = params["properties"]["params"]["$ref"]
                ref_name = ref_path.split("/")[-1]
                schema = params["$defs"].get(ref_name, {})
                return {
                    "type": "object",
                    "properties": {
                        "params": {
                            "type": "object",
                            "properties": schema.get("properties", {}),
                            "required": schema.get("required", []),
                            "description": schema.get("description", "")
                        }
                    },
                    "required": ["params"]
                }
            else:
                return params

        tools = []
        for tool in tool_list:
            expanded_parameters = expand_parameters(tool.parameters)
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "No description provided.",
                    "parameters": expanded_parameters
                }
            })
        # [t for t in tools if t["function"]["name"] in ["GetTimeSeriesAdd", "GetTimeSeriesAd"]]
        return tools

    all_tools = server._tool_manager._tools
    server._tool_manager._tools = {}  # leave only u-tool

    db = lancedb.connect(DB_PATH)
    table = db.open_table("endpoints")
    table_df = table.to_pandas()
    tool_plan_map = ToolPlanMap(table_df)

    @server.tool(name="u-tool")
    async def u_tool(
        query: str,
        ctx: Context,
        format: Optional[str] = None,
        plan: Optional[str] = None,
    ) -> UToolResponse:
        """
        A universal tool router for the MCP system, designed for the Twelve Data API.

        This tool accepts a natural language query in English and performs the following:
        1. Uses vector search to retrieve the top-N relevant Twelve Data endpoints.
        2. Sends the query and tool descriptions to OpenAI's gpt-4o with function calling.
        3. The model selects the most appropriate tool and generates the input parameters.
        4. The selected endpoint (tool) is executed and its response is returned.

        Supported endpoint categories (from Twelve Data docs):
        - Market & Reference: price, quote, symbol_search, stocks, exchanges, market_state
        - Time Series: time_series, eod, splits, dividends, etc.
        - Technical Indicators: rsi, macd, ema, bbands, atr, vwap, and 100+ others
        - Fundamentals & Reports: earnings, earnings_estimate, income_statement,
          balance_sheet, cash_flow, statistics, profile, ipo_calendar, analyst_ratings
        - Currency & Crypto: currency_conversion, exchange_rate, price_target
        - Mutual Funds / ETFs: funds, mutual_funds/type, mutual_funds/world
        - Misc Utilities: logo, calendar endpoints, time_series_calendar, etc.
        """
        o_ai_api_key_to_use: Optional[str]
        if transport == 'stdio':
            if u_tool_open_ai_api_key is not None:
                o_ai_api_key_to_use = u_tool_open_ai_api_key
            else:
                # It's not a possible case
                return constructor_for_utool(
                    error=(
                        f"Transport is stdio and u_tool_open_ai_api_key is None. "
                        f"Something goes wrong. Please contact support."
                    ),
                )
        elif transport == "streamable-http":
            if u_tool_open_ai_api_key is not None:
                o_ai_api_key_to_use=u_tool_open_ai_api_key
            else:
                rc: RequestContext = ctx.request_context
                token_from_rc = get_tokens_from_rc(rc=rc)
                if token_from_rc.error is not None:
                    return constructor_for_utool(error=token_from_rc.error)
                elif token_from_rc.twelve_data_api_key and token_from_rc.open_ai_api_key:
                    o_ai_api_key_to_use = token_from_rc.open_ai_api_key
                else:
                    return constructor_for_utool(error=f"Either OPEN API KEY or TWELVE Data API key is not provided.")
        else:
            return constructor_for_utool(error=f"This transport is not supported")

        client = openai.OpenAI(api_key=o_ai_api_key_to_use)
        all_candidate_ids: List[str]

        try:
            embedding = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=[query]
            ).data[0].embedding

            results = table.search(embedding).metric("cosine").limit(TOP_N).to_list()  # type: ignore[attr-defined]
            all_candidate_ids = [r["id"] for r in results]
            if "GetTimeSeries" not in all_candidate_ids:
                all_candidate_ids.append('GetTimeSeries')

            candidates, premium_only_candidates = tool_plan_map.split(
                user_plan=plan, tool_operation_ids=all_candidate_ids
            )

        except Exception as e:
            return constructor_for_utool(error=f"Embedding or vector search failed: {e}")

        filtered_tools = [tool for tool in all_tools.values() if tool.name in candidates]  # type: ignore
        openai_tools = build_openai_tools_subset(filtered_tools)

        prompt = (
            "You are a function-calling assistant. Based on the user query, "
            "you must select the most appropriate function from the provided tools and return "
            "a valid tool call with all required parameters. "
            "Before the function call, provide a brief plain-text explanation (1–2 sentences) of "
            "why you chose that function, based on the user's intent and tool descriptions."
        )

        try:
            llm_response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    cast(ChatCompletionSystemMessageParam, {"role": "system", "content": prompt}),
                    cast(ChatCompletionSystemMessageParam, {"role": "user", "content": query}),
                ],
                tools=openai_tools,
                tool_choice="required",
                temperature=0,
            )

            call = llm_response.choices[0].message.tool_calls[0]
            name = call.function.name
            arguments = json.loads(call.function.arguments)
            # all tools require single parameter with nested attributes, but sometimes LLM flattens it
            if "params" not in arguments:
                arguments = {"params": arguments}

        except Exception as e:
            return constructor_for_utool(
                top_candidates=candidates,
                premium_only_candidates=premium_only_candidates,
                error=f"LLM did not return valid tool call: {e}",
            )

        tool = all_tools.get(name)
        if not tool:
            return constructor_for_utool(
                top_candidates=candidates,
                premium_only_candidates=premium_only_candidates,
                selected_tool=name,
                param=arguments,
                error=f"Tool '{name}' not found in MCP",
            )

        try:
            params_type = tool.fn_metadata.arg_model.model_fields["params"].annotation
            arguments['params'] = params_type(**arguments['params'])
            arguments['ctx'] = ctx

            result = await tool.fn(**arguments)

            if format == "md":
                result = get_md_response(
                    client=client,
                    llm_model=llm_model,
                    query=query,
                    result=result,
                )

            return constructor_for_utool(
                top_candidates=candidates,
                premium_only_candidates=premium_only_candidates,
                selected_tool=name,
                param=arguments,
                response=result,
            )
        except Exception as e:
            return constructor_for_utool(
                top_candidates=candidates,
                premium_only_candidates=premium_only_candidates,
                selected_tool=name,
                param=arguments,
                error=str(e),
            )

    if transport == "streamable-http":
        @server.custom_route("/utool", ["GET"])
        async def u_tool_http(request: Request):
            query = request.query_params.get("query")
            format_param = request.query_params.get("format", default="json").lower()
            user_plan_param = request.query_params.get("plan", None)
            if not query:
                return JSONResponse({"error": "Missing 'query' query parameter"}, status_code=400)

            request_context = create_dummy_request_context(request)
            ctx = Context(request_context=request_context)
            result = await u_tool(
                query=query, ctx=ctx,
                format=format_param,
                plan=user_plan_param
            )

            return JSONResponse(content=result.model_dump(mode="json"))

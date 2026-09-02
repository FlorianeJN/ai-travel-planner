from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agent.prompts import SYSTEM_PROMPT
from agent.state import TravelState
from core.mcp_client import load_mcp_tools

load_dotenv()


async def build_travel_graph():
    tools = await load_mcp_tools()

    # Universal model initialization bound with tools
    llm = init_chat_model(
        "gemini-3.5-flash-lite", model_provider="google_genai", temperature=0.2
    )
    llm_with_tools = llm.bind_tools(tools)

    # Reasoning Node
    async def planner_node(state: TravelState):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # Conditional Edge
    def should_continue(state: TravelState) -> str:
        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", None):
            return "tools"
        return END

    # Graph Wiring
    graph = StateGraph(TravelState)
    graph.add_node("planner", planner_node)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "planner")
    graph.add_conditional_edges("planner", should_continue, ["tools", END])
    graph.add_edge("tools", "planner")

    return graph.compile()

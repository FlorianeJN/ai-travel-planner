from langgraph.graph import StateGraph, START, END
from agent.state import TravelState
from agent.nodes import (
    parse_input_node,
    make_weather_node,
    make_activities_node,
    synthetizer_node,
    make_logistics_node,
)

from core.mcp_client import load_mcp_tools


def split_tools(tools: list) -> tuple[list, list, list]:
    weather_tool_names = {"get_city_coordinates", "get_weather"}
    activity_tool_names = {"search_activities"}
    logistics_tools_name = {"search_travel_costs", "convert_price"}

    weather_tools = [t for t in tools if t.name in weather_tool_names]
    activity_tools = [t for t in tools if t.name in activity_tool_names]
    logistics_tools = [t for t in tools if t.name in logistics_tools_name]

    return weather_tools, activity_tools, logistics_tools


async def build_graph():
    tools = await load_mcp_tools()
    weather_tools, activity_tools, logistics_tools = split_tools(tools)

    weather_node = make_weather_node(weather_tools)
    activities_node = make_activities_node(activity_tools)
    logistics_node = make_logistics_node(logistics_tools)

    graph = StateGraph(TravelState)

    graph.add_node("parse_input", parse_input_node)
    graph.add_node("weather", weather_node)
    graph.add_node("activities", activities_node)
    graph.add_node("logistics", logistics_node)
    graph.add_node("synthesizer", synthetizer_node)

    graph.add_edge(START, "parse_input")
    graph.add_edge("parse_input", "weather")
    graph.add_edge("parse_input", "activities")
    graph.add_edge("parse_input", "logistics")
    graph.add_edge("weather", "synthesizer")
    graph.add_edge("activities", "synthesizer")
    graph.add_edge("logistics", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()

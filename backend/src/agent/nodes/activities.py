from langchain_core.messages import HumanMessage
from agent.llm import get_llm
from agent.state import TravelState


def make_activities_node(activity_tools: list):
    llm_activities = get_llm().bind_tools(activity_tools)
    tools_by_name = {tool.name: tool for tool in activity_tools}

    async def activities_node(state: TravelState) -> dict:
        dest = state.get("destination")
        dates = state.get("dates") or "unspecified"
        budget = state.get("budget_limit")

        budget_line = f"Trip budget: {budget}." if budget else "No budget specified."

        prompt = (
            f"Find activities and attractions to do in {dest} for a trip on these dates: {dates}. "
            f"{budget_line}\n"
            "Decide how many activities to search for based on the trip length and budget — "
            "roughly 1-3 activities per day of the trip is a reasonable guide, up to a maximum of 20 total. "
            "A short trip or tight budget needs fewer options; a longer trip or higher budget needs more variety. "
            "Include a mix of budget-friendly and premium options with prices and descriptions."
        )
        response = await llm_activities.ainvoke([HumanMessage(content=prompt)])

        if not response.tool_calls:
            return {"itinerary": []}

        call = response.tool_calls[0]
        tool = tools_by_name.get(call["name"])
        if tool is None:
            return {"itinerary": []}

        tool_result = await tool.ainvoke(call["args"])
        return {"itinerary": tool_result}

    return activities_node

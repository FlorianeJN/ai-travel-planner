from agent.llm import get_llm
from agent.state import TravelState
from schemas.travel import FinalItinerary
from langchain.messages import HumanMessage
from typing import cast


async def synthetizer_node(state: TravelState) -> dict:
    llm_structured = get_llm().with_structured_output(FinalItinerary)
    dest = state.get("destination")
    origin = state.get("origin")
    currency = state.get("base_currency", "CAD")
    dates = state.get("dates")
    budget = state.get("budget_limit")
    weather = state.get("weather_forecast")
    logistics = state.get("logistics")
    messages = state.get("messages", [])

    budget_instruction = ""
    if budget:
        budget_instruction = f"""\
    IMPORTANT — Budget Utilization:
    The maximum budget is {budget} {currency}. Your goal is to get as close to this amount as possible, \
    NOT to minimize expenses. A trip costing {budget * 0.5} {currency} when the budget is {budget} {currency} \
    is a POOR result — you are underutilizing the available budget.

    Add more activities, propose more premium options (better restaurants, more comprehensive activities, \
    higher-quality hotels) to use the budget optimally, while staying under the {budget} {currency} limit. \
    Aim to utilize at least 85-95% of the total budget (transport + hotel + activities combined).
    """

    prompt = f"""\
    You are an expert travel planner. Generate the complete final itinerary for a trip from \
    {origin or 'not specified'} to {dest}.

    Travel dates: {dates or 'not specified'}
    Expected currency: {currency}
    {budget_instruction}
    Expected weather: 
    {weather}

    Logistics estimates (transport + hotel): 
    {logistics}

    Based on this information, detail the weather and propose a coherent activity plan with \
    estimated prices, including the transport/hotel estimates.\
    """

    itinerary_result = cast(
        FinalItinerary,
        await llm_structured.ainvoke([*messages, HumanMessage(content=prompt)]),
    )

    return {
        "next_step": "completed",
        "messages": [HumanMessage(content=itinerary_result.model_dump_json(indent=2))],
    }

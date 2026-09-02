from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from agent.llm import get_llm
from agent.state import TravelState


class LogisticsResult(BaseModel):
    transport_mode: str | None = Field(
        default=None,
        description="Recommended mode of transport: 'plane', 'train', 'car', 'bus', etc.",
    )
    transport_estimate: str | None = Field(
        default=None,
        description="Estimated transport price, converted to the target currency",
    )
    hotel_estimate: str | None = Field(
        default=None,
        description="Estimated hotel price, converted to the target currency",
    )
    currency: str = Field(description="Currency in which the estimates are expressed")
    within_budget: bool | None = Field(
        default=None,
        description="True if the estimated total respects the given budget, otherwise False. None if no budget was provided.",
    )


LOGISTICS_SYSTEM_PROMPT = """You are an expert travel logistics specialist. Mandatory steps:
1. First, evaluate whether the route between the origin and the destination requires a flight. For short trips or between nearby cities (e.g., same region, same province, a few hours drive), prioritize a ground transport estimate (train, car, bus) over a flight.
2. Search for price estimates for the transport (adapted to the route) and the hotel.
3. If the prices found are not already in the target currency, convert them using the conversion tool.
4. If a maximum budget is provided, compare the total to the budget and indicate if the trip is within budget.
Stop immediately once you have the converted estimates."""


def make_logistics_node(logistics_tools: list):
    logistics_agent = create_agent(
        model=get_llm(),
        tools=logistics_tools,
        system_prompt=LOGISTICS_SYSTEM_PROMPT,
        response_format=LogisticsResult,
    )

    async def logistics_node(state: TravelState) -> dict:
        origin = state.get("origin") or "non précisée"
        destination = state["destination"]
        dates = state.get("dates") or "non précisées"
        currency = state.get("base_currency", "CAD")
        budget = state.get("budget_limit")

        budget_line = (
            f"Budget maximal : {budget} {currency}."
            if budget
            else "Aucun budget spécifié."
        )

        prompt = (
            f"Estime le coût du voyage de {origin} à {destination} pour les dates suivantes : {dates}. "
            f"Devise cible : {currency}. {budget_line}"
        )

        result = await logistics_agent.ainvoke(
            {"messages": [HumanMessage(content=prompt)]}
        )

        structured = result["structured_response"]
        if not isinstance(structured, LogisticsResult):
            raise TypeError(f"Expected LogisticsResult, got {type(structured)}")

        logistics_dict = structured.model_dump(exclude={"within_budget"})
        return {
            "logistics": logistics_dict,
            "next_step": "over_budget" if structured.within_budget is False else None,
        }

    return logistics_node

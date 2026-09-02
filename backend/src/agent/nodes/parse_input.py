from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from src.agent.llm import get_llm
from src.agent.state import TravelState
from typing import cast


class ExtractedTripInfo(BaseModel):
    destination: str = Field(description="Extracted target city or country")
    origin: str | None = Field(
        default=None, description="Extracted starting city, country, or location"
    )
    dates: str | None = Field(
        default=None,
        description="Dates or travel period as mentioned (e.g., 'from June 15 to 22, 2026')",
    )
    budget_limit: float | None = Field(
        default=None,
        description="Maximum mentioned budget, numerical value only (e.g., 3000 for '$3000')",
    )
    base_currency: str = Field(
        default="CAD", description="Detected primary currency (e.g., CAD, EUR, USD)"
    )


PARSER_SYSTEM_PROMPT = """Extract the following information from the user's message regarding their trip:
- destination (mandatory)
- origin (departure city/country, if mentioned)
- dates (if mentioned)
- budget_limit (numerical amount only, if a budget is mentioned)
- base_currency (detected currency, default is CAD if not specified)
Leave the fields empty if the information is not present in the message."""


async def parse_input_node(state: TravelState) -> dict:
    llm = get_llm().with_structured_output(ExtractedTripInfo)
    last_user_message = state["messages"][-1].content

    extracted = cast(
        ExtractedTripInfo,
        await llm.ainvoke(
            [
                SystemMessage(content=PARSER_SYSTEM_PROMPT),
                HumanMessage(content=last_user_message),
            ]
        ),
    )

    return {
        "destination": extracted.destination,
        "origin": extracted.origin,
        "dates": extracted.dates,
        "budget_limit": extracted.budget_limit,
        "base_currency": extracted.base_currency,
    }

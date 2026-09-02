from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from agent.llm import get_llm
from agent.state import TravelState

WEATHER_AGENT_SYSTEM_PROMPT = """You are an expert Weather Specialist specialized in retrieving accurate forecasts for travel planning.

Your goal is to provide precise weather conditions for the exact dates of a trip using your tools.

### Operational Guidelines:
1. **Mandatory Geocoding Phase**:
   - Find the exact GPS coordinates of the destination using the geocoding tool.

2. **Forecasting Logistics**:
   - Use these coordinates to retrieve the expected weather for the specific trip dates (not the current weather).

3. **Output Discipline**:
   - If the tool only provides current weather or short-term forecasts that do not cover the trip dates, state this clearly (`is_forecast_reliable=False`) rather than presenting current weather as reliable for those dates.
   - Stop immediately once you have the required information; do not perform any other actions.
"""


class WeatherResult(BaseModel):
    summary: str = Field(description="Natural language summary of the expected weather")
    temperature_range: str | None = Field(default=None, description="Ex: '18-24°C'")
    conditions: str | None = Field(
        default=None, description="Ex: 'sunny, scattered showers'"
    )
    is_forecast_reliable: bool = Field(
        description="False if the tool only provides current weather and not the weather for the trip dates"
    )


def make_weather_node(weather_tools: list):
    weather_agent = create_agent(
        model=get_llm(),
        tools=weather_tools,
        system_prompt=WEATHER_AGENT_SYSTEM_PROMPT,
        response_format=WeatherResult,
    )

    async def weather_node(state: TravelState) -> dict:
        destination = state["destination"]
        dates = state["dates"] or "undefined"

        prompt = f"Expected weather in {destination} for the following dates: {dates}."

        result = await weather_agent.ainvoke(
            {"messages": [HumanMessage(content=prompt)]}
        )

        structured = result["structured_response"]
        if not isinstance(structured, WeatherResult):
            raise TypeError(f"Expected WeatherResult, got {type(structured)}")

        return {"weather_forecast": structured.model_dump()}

    return weather_node

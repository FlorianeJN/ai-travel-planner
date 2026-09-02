import json
from fastmcp import FastMCP
from tools import (
    convert_currency,
    fetch_weather,
    geocode,
    search_activities_web,
    search_logistics_web,
)

mcp = FastMCP("TravelTools")


@mcp.tool()
async def get_city_coordinates(city: str) -> str:
    """Converts a city name into GPS coordinates {latitude, longitude}."""
    data = await geocode(city)
    return json.dumps(data)


@mcp.tool()
async def get_weather(latitude: float, longitude: float) -> str:
    """Gets current weather conditions using latitude and longitude."""
    data = await fetch_weather(latitude, longitude)
    return json.dumps(data)


@mcp.tool()
def search_activities(city: str, query: str = "top attractions ticket prices") -> str:
    """Searches the web for local activities with prices and descriptions."""
    data = search_activities_web(city, query)
    return json.dumps(data)


@mcp.tool()
def search_travel_costs(
    origin: str, destination: str, target_date: str = "", transport_mode: str = "flight"
) -> str:
    """Searches for price estimates for transport (flight, train, car, bus)
    and hotel between two cities. Choose transport_mode based on distance/relevance of the route
    (e.g., 'flight' for long distances, 'train' or 'bus' for short trips between nearby cities).
    """
    data = search_logistics_web(origin, destination, target_date, transport_mode)
    return json.dumps(data)


@mcp.tool()
async def convert_price(amount: float, from_curr: str, to_curr: str) -> str:
    """Converts a price from one currency to another (e.g., USD to CAD, JPY to CAD)."""
    data = await convert_currency(amount, from_curr, to_curr)
    return json.dumps(data)


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=5000)

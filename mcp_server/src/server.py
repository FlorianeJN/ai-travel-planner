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
    """Convertit un nom de ville en coordonnées GPS {latitude, longitude}."""
    data = await geocode(city)
    return json.dumps(data)


@mcp.tool()
async def get_weather(latitude: float, longitude: float) -> str:
    """Obtient les conditions météo actuelles avec la latitude et la longitude."""
    data = await fetch_weather(latitude, longitude)
    return json.dumps(data)


@mcp.tool()
def search_activities(city: str, query: str = "top attractions ticket prices") -> str:
    """Recherche sur le web des activités locales avec tarifs et descriptions."""
    data = search_activities_web(city, query)
    return json.dumps(data)


@mcp.tool()
def search_travel_costs(origin: str, destination: str, target_date: str = "") -> str:
    """Recherche des estimations de prix pour les vols et les hôtels entre deux villes."""
    data = search_logistics_web(origin, destination, target_date)
    return json.dumps(data)


@mcp.tool()
async def convert_price(amount: float, from_curr: str, to_curr: str) -> str:
    """Convertit un prix d'une devise à une autre (ex: USD à CAD, JPY à CAD)."""
    data = await convert_currency(amount, from_curr, to_curr)
    return json.dumps(data)


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=5000)

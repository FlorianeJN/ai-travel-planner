import os
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_activities_web(
    city: str, query: str = "top attractions ticket prices"
) -> list:
    """Recherche des activités locales et coûts d'entrée."""
    res = tavily_client.search(
        query=f"{city} {query}",
        search_depth="basic",
        max_results=4,
    )
    return [
        {"title": r["title"], "content": r["content"]} for r in res.get("results", [])
    ]


def search_logistics_web(origin: str, destination: str, target_date: str = "") -> dict:
    """Estime les coûts moyens de vols et d'hôtels via le web."""
    flight_query = (
        f"average roundtrip flight price {origin} to {destination} {target_date}"
    )
    hotel_query = f"average hotel price per night in {destination}"

    flight_res = tavily_client.search(query=flight_query, max_results=2)
    hotel_res = tavily_client.search(query=hotel_query, max_results=2)

    return {
        "flight_snippets": [r["content"] for r in flight_res.get("results", [])],
        "hotel_snippets": [r["content"] for r in hotel_res.get("results", [])],
    }

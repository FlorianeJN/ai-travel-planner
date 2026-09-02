import os
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_activities_web(
    city: str, query: str = "top attractions ticket prices"
) -> list:
    """Search for local activities and entrance costs."""
    res = tavily_client.search(
        query=f"{city} {query}",
        search_depth="basic",
        max_results=20,
    )
    return [
        {"title": r["title"], "content": r["content"]} for r in res.get("results", [])
    ]


def search_logistics_web(
    origin: str,
    destination: str,
    target_date: str = "",
    transport_mode: str = "flight",
) -> dict:
    """Estimates average transport and hotel costs via the web."""
    transport_query = (
        f"average {transport_mode} price {origin} to {destination} {target_date}"
    )
    hotel_query = f"average hotel price per night in {destination}"

    transport_res = tavily_client.search(query=transport_query, max_results=2)
    hotel_res = tavily_client.search(query=hotel_query, max_results=2)

    return {
        "transport_mode": transport_mode,
        "transport_snippets": [r["content"] for r in transport_res.get("results", [])],
        "hotel_snippets": [r["content"] for r in hotel_res.get("results", [])],
    }

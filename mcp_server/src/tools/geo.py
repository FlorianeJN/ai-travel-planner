import httpx


async def geocode(city: str) -> dict:
    """Converts a city name into GPS coordinates."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=10.0)
        data = res.json()
        if not data.get("results"):
            return {}
        first = data["results"][0]
        return {
            "name": first.get("name"),
            "country": first.get("country", ""),
            "latitude": first.get("latitude"),
            "longitude": first.get("longitude"),
        }


async def fetch_weather(lat: float, lon: float) -> dict:
    """Fetches the current weather conditions via Open-Meteo."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=10.0)
        if res.status_code != 200:
            return {"error": "Unable to reach the weather API"}
        return res.json().get("current_weather", {})

# MCP Server

The MCP server exposes the external tools used by the backend to gather information about destinations, weather, activities, and logistics costs. It acts as a standardized layer between agent orchestration and third-party APIs.

## Service role

The server contains the tools needed to:

- geocode a city into GPS coordinates,
- retrieve weather data through Open-Meteo,
- search for activities and pricing,
- estimate transportation and accommodation costs,
- convert amounts between currencies.

## Tech stack

- Python 3.11
- FastMCP
- HTTPX
- Tavily API
- Open-Meteo
- Frankfurter API

## Project structure

```text
mcp_server/
├── src/
│   ├── server.py
│   └── tools/
│       ├── __init__.py
│       ├── finance.py
│       ├── geo.py
│       └── search.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Exposed tools

The server exposes the following tools through FastMCP:

### `get_city_coordinates(city: str) -> str`

Converts a city name into GPS coordinates. Returns JSON as a string.

### `get_weather(latitude: float, longitude: float) -> str`

Retrieves current weather conditions through Open-Meteo for a given latitude and longitude.

### `search_activities(city: str, query: str = "top attractions ticket prices") -> str`

Searches for local activities through Tavily along with descriptions and approximate prices.

### `search_travel_costs(origin: str, destination: str, target_date: str = "", transport_mode: str = "flight") -> str`

Looks up price estimates for transport and hotels between two cities. The transport mode can be flight, train, car, or bus.

### `convert_price(amount: float, from_curr: str, to_curr: str) -> str`

Converts an amount from one currency to another using Frankfurter.

## Implementation

### `src/server.py`

The server is initialized with:

```python
mcp = FastMCP("TravelTools")
```

and then exposes each tool using the `@mcp.tool()` decorator.

The server is configured to listen on:

- 0.0.0.0:5000
- SSE mode (`transport="sse"`)

### `src/tools/geo.py`

- `geocode()`: calls the Open-Meteo geocoding API,
- `fetch_weather()`: calls the Open-Meteo weather API.

### `src/tools/search.py`

- `search_activities_web()`: performs a Tavily search for attractions,
- `search_logistics_web()`: searches for transport and hotel prices.

### `src/tools/finance.py`

- `convert_currency()`: converts currency amounts via Frankfurter.

## Prerequisites

- Python 3.11+
- uv
- a `.env` file containing at least:

```env
TAVILY_API_KEY=...
```

## Local startup

From `mcp_server`:

```bash
uv sync
uv run python src/server.py
```

The server is available at:

- http://localhost:5000

## Startup via Docker Compose

From the repository root:

```bash
docker compose up --build
```

The MCP service is exposed at:

- http://localhost:5000/sse

## Integration with the backend

The backend loads MCP tools via `langchain_mcp_adapters`:

```python
MultiServerMCPClient({"travel_tools": {"transport": "sse", "url": MCP_URL}})
```

The backend connects to the MCP server through the environment variable:

```env
MCP_SERVER_URL=http://mcp_server:5000/sse
```

## Notes

- Results are returned as JSON strings to simplify communication between the MCP server and LangChain agents.
- This service is intentionally lightweight: it contains no trip-planning logic or graph orchestration, only the tools required by the agents.
- The MCP layer standardizes how agents interact with the outside world.

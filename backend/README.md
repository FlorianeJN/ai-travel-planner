# Backend

The backend is the application logic and orchestration service for the travel planner. It exposes a FastAPI API, builds the LangGraph agent graph, loads remote MCP tools, and synthesizes a final itinerary based on weather, activity, and logistics results.

## Service role

This service is responsible for:

- analyzing the user message through a parsing node,
- extracting travel information (destination, dates, budget, currency, origin),
- retrieving data through an external MCP server,
- composing a structured final itinerary,
- exposing HTTP endpoints to clients.

## Internal architecture

### LangGraph flow
The main flow is defined in `src/agent/graph.py`:

- `parse_input`: extracts parameters from the message,
- `weather`: queries geocoding and weather tools,
- `activities`: searches for activities and attractions,
- `logistics`: estimates transport and hotel costs,
- `synthesizer`: builds the final itinerary.

The graph then ends at `END`.

### Key components

- `src/main.py`: FastAPI entry point.
- `src/api/travel.py`: API routes and SSE streaming.
- `src/agent/state.py`: graph state definition.
- `src/agent/llm.py`: Gemini LLM configuration through LangChain.
- `src/core/mcp_client.py`: MCP client that loads tools from the remote server.
- `src/agent/nodes/*`: specialized nodes for weather, activities, logistics, and synthesis.
- `src/schemas/travel.py`: Pydantic schemas for the final itinerary.

## Tech stack

- Python 3.11
- FastAPI
- LangGraph
- LangChain
- Google GenAI / Gemini
- Model Context Protocol (MCP)
- uv for dependency management
- SQLite via the graph state (through LangGraph checkpointer), if the project is extended

## Prerequisites

- Python 3.11+
- uv
- a Google API key for Gemini
- a Tavily API key for the MCP server (used by search tools)
- a `.env` file at the project root

## Environment variables

The backend reads environment settings via `python-dotenv` and the Docker Compose configuration. At minimum:

```env
GOOGLE_API_KEY=...
TAVILY_API_KEY=...
MCP_SERVER_URL=http://mcp_server:5000/sse
```

In local non-Docker environments, the default is usually:

```env
MCP_SERVER_URL=http://localhost:5000/sse
```

## Local startup

From the `backend` folder:

```bash
uv sync
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The service is then available at:

- http://localhost:8000

## Startup via Docker Compose

From the repository root:

```bash
docker compose up --build
```

The backend is exposed at:

- http://localhost:8000

## API

The router is mounted under `/api/v1/travel`.

### 1) Simple trip plan generation

```http
POST /api/v1/travel/plan
Content-Type: application/json
```

Body:

```json
{
  "message": "Plan a 3-day trip to Paris from Montreal with a budget of 2500 CAD"
}
```

Response: an SSE stream with events such as:

- `step`: graph progress by node
- `done`: processing complete
- `error`: encountered error

### 2) Synchronous trip plan generation

```http
POST /api/v1/travel/plan/sync
Content-Type: application/json
```

Body:

```json
{
  "message": "Plan a weekend trip to Kyoto from Vancouver under 1800 CAD"
}
```

Returns a final JSON object containing:

- destination,
- origin,
- dates,
- budget,
- weather,
- logistics,
- final itinerary.

### 3) Structured trip generation

```http
POST /api/v1/travel/plan/structured
Content-Type: application/json
```

Body:

```json
{
  "destination": "Tokyo",
  "origin": "Montreal",
  "start_date": "2026-06-10",
  "end_date": "2026-06-16",
  "budget_limit": 2600,
  "base_currency": "CAD"
}
```

## Example curl request

```bash
curl -X POST http://localhost:8000/api/v1/travel/plan \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 4-day trip to Lisbon from Toronto with a budget of 2200 CAD"}'
```

## Design notes

- The backend does not call external search or weather APIs directly; it goes through the standard MCP interface.
- Tools are loaded dynamically through `MultiServerMCPClient`.
- The service is designed to be extensible: a new tool or node type can be added without fundamentally changing the graph.

## Important considerations

- The weather and logistics nodes use LangChain agents with MCP tools.
- Results are not always complete historical data for a future date; the code explicitly handles this using `is_forecast_reliable` in the weather model.
- The final itinerary is synthesized from sub-agent results and the overall trip state.

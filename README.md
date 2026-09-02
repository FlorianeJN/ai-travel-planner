# AI Travel Planner

Agentic travel planning system built around Python, LangGraph, FastAPI, and the Model Context Protocol (MCP). The application turns a user request into a structured itinerary by relying on specialized tools for weather, activities, logistics costs, and currency conversion.

## Overview

The architecture is intentionally split into two services:

1. `backend`: orchestrates the agent flow, extracts travel information, calls MCP tools, and synthesizes the final itinerary.
2. `mcp_server`: exposes external tools through the MCP standard, including geocoding, web search, weather retrieval, and currency conversion.

## Functional architecture

The typical flow is as follows:

1. A client sends an API request to the backend.
2. The `parse_input` node extracts the destination, dates, budget, and currency.
3. The `weather`, `activities`, and `logistics` nodes use MCP tools to gather the relevant information.
4. The `synthesizer` node assembles a coherent final travel plan.
5. The backend responds to the client using standard JSON or the SSE stream.

## Repository structure

```text
ai-travel-planner/
├── backend/
│   ├── src/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
├── mcp_server/
│   ├── src/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
├── docker-compose.yml
├── .env
├── README.md
└── .gitignore
```

## Tech stack

- Python 3.11
- FastAPI
- LangGraph / LangChain
- Google GenAI (Gemini)
- FastMCP
- Open-Meteo
- Tavily
- Frankfurter API
- Docker / Docker Compose
- uv

## Quick start

### 1) Prepare environment variables

Make sure you have a `.env` file at the repository root with at least:

```env
GOOGLE_API_KEY=...
TAVILY_API_KEY=...
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT="ai-trip-planner"
```

### 2) Start all services

```bash
docker compose up --build
```

The services then run at:

- Backend: http://localhost:8000
- MCP Server: http://localhost:5000/sse

## Local startup without Docker

### Backend

```bash
cd backend
uv sync
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### MCP Server

```bash
cd mcp_server
uv sync
uv run python src/server.py
```

## Main API

The backend exposes the following endpoints:

- `POST /api/v1/travel/plan`: streaming trip planning via SSE
- `POST /api/v1/travel/plan/sync`: synchronous trip planning
- `POST /api/v1/travel/plan/structured`: structured generation from typed fields

Example:

```bash
curl -X POST http://localhost:8000/api/v1/travel/plan \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 3-day trip to Kyoto from Montreal under 2000 CAD"}'
```

## The two projects in detail

### Backend

The backend is the core product. It contains:

- the FastAPI API,
- the main planning graph,
- request analysis nodes,
- specialized weather / activities / logistics agents,
- final itinerary synthesis.

See also: [backend/README.md](backend/README.md)

### MCP Server

The MCP server provides external access tools:

- city geocoding,
- weather and climate data,
- tourist activity search,
- travel cost estimation,
- currency conversion.

See also: [mcp_server/README.md](mcp_server/README.md)

## Key design points

- The backend does not call external APIs directly; it relies on the MCP tools exposed by the server.
- Data is standardized through JSON and the backend's Pydantic models.
- Orchestration is modular so new agents and data sources can be added without redesigning the whole system.
- Tools can be replaced or extended without changing the HTTP endpoint contracts.

## Development and maintenance

To evolve the system:

- add new tools in the MCP server when a new data source is needed,
- add graph nodes in the backend to introduce additional reasoning steps,
- enrich the Pydantic schemas to produce more structured outputs.

## Notes

- Travel planning logic relies heavily on LLM reasoning and the capabilities of LangChain / LangGraph.
- Performance and output quality depend on the external API keys and third-party services available.
- The project is designed as an agentic application prototype with a clear separation between orchestration and tool access.

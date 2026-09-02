import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, BaseMessage
from pydantic import BaseModel
from agent.graph import build_graph
from agent.state import TravelState

router = APIRouter()


class PlanRequest(BaseModel):
    message: str


class StructuredPlanRequest(BaseModel):
    destination: str
    origin: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    budget_limit: float | None = None
    base_currency: str = "CAD"


def _build_initial_state(user_message: str) -> TravelState:
    return {
        "messages": [HumanMessage(content=user_message)],
        "destination": None,
        "origin": None,
        "dates": None,
        "budget_limit": None,
        "base_currency": "CAD",
        "weather_forecast": None,
        "logistics": None,
        "itinerary": None,
        "next_step": None,
    }


def _build_prompt_from_fields(
    destination: str,
    origin: str | None,
    start_date: str | None,
    end_date: str | None,
    budget_limit: float | None,
    base_currency: str,
) -> str:
    lines = [f"Destination: {destination}"]

    if origin:
        lines.append(f"Origin: {origin}")

    if start_date and end_date:
        lines.append(f"Dates: from {start_date} to {end_date}")
    elif start_date:
        lines.append(f"Start date: {start_date}")
    elif end_date:
        lines.append(f"End date: {end_date}")
    else:
        lines.append("Dates: not specified")

    if budget_limit:
        lines.append(f"Budget: {budget_limit} {base_currency}")
    else:
        lines.append("Budget: not specified")

    return "Plan a trip with the following details:\n" + "\n".join(lines)


def _format_result(result: dict) -> dict:
    return {
        "destination": result.get("destination"),
        "origin": result.get("origin"),
        "dates": result.get("dates"),
        "budget_limit": result.get("budget_limit"),
        "weather_forecast": result.get("weather_forecast"),
        "logistics": result.get("logistics"),
        "itinerary": result["messages"][-1].content,
    }


def _serialize_node_output(output: dict) -> dict:
    serialized = {}
    for key, value in output.items():
        if isinstance(value, list) and value and isinstance(value[0], BaseMessage):
            serialized[key] = [
                {"role": msg.type, "content": msg.content} for msg in value
            ]
        elif isinstance(value, BaseMessage):
            serialized[key] = {"role": value.type, "content": value.content}
        else:
            serialized[key] = value
    return serialized


def format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def stream_travel_plan(user_message: str):
    app_graph = await build_graph()
    initial_state = _build_initial_state(user_message)

    try:
        async for update in app_graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in update.items():
                safe_output = _serialize_node_output(node_output)
                yield format_sse("step", {"node": node_name, "output": safe_output})

        yield format_sse("done", {"status": "completed"})

    except Exception as e:
        yield format_sse("error", {"message": str(e)})


@router.post("/plan")
async def plan_trip(payload: PlanRequest):
    return StreamingResponse(
        stream_travel_plan(payload.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/plan/sync")
async def plan_trip_sync(payload: PlanRequest):
    app_graph = await build_graph()
    initial_state = _build_initial_state(payload.message)

    result = await app_graph.ainvoke(initial_state)

    return _format_result(result)


@router.post("/plan/structured")
async def plan_trip_structured(payload: StructuredPlanRequest):
    prompt = _build_prompt_from_fields(
        destination=payload.destination,
        origin=payload.origin,
        start_date=payload.start_date,
        end_date=payload.end_date,
        budget_limit=payload.budget_limit,
        base_currency=payload.base_currency,
    )

    app_graph = await build_graph()
    initial_state = _build_initial_state(prompt)

    result = await app_graph.ainvoke(initial_state)

    return _format_result(result)

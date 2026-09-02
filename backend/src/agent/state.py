from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class Activity(TypedDict):
    title: str
    description: str
    cost_estimated: float
    currency: str


class DailyPlan(TypedDict):
    day_number: int
    date: Optional[str]
    theme: str
    activities: List[Activity]
    notes: Optional[str]


class LogisticsEstimate(TypedDict):
    flight_estimate: Optional[str]
    hotel_estimate: Optional[str]
    currency: str


class TravelState(TypedDict):
    # Historique des messages LangChain (user, ai, tool calls)
    messages: Annotated[List[BaseMessage], add_messages]

    # Données extraites et partagées
    destination: Optional[str]
    origin: Optional[str]
    dates: Optional[str]
    budget_limit: Optional[float]
    base_currency: str

    # Résultats des nœuds spécialisés
    weather_forecast: Optional[dict]
    logistics: Optional[LogisticsEstimate]
    itinerary: Optional[List[DailyPlan]]

    # Métadonnées de contrôle de flux
    next_step: Optional[str]

from typing import List
from pydantic import BaseModel, Field


class ActivityDetail(BaseModel):
    title: str = Field(description="Name of the attraction or activity")
    description: str = Field(description="Short description and why it is recommended")
    estimated_cost: float = Field(description="Estimated cost per person (0 if free)")
    currency: str = Field(description="Currency code (e.g., CAD, EUR, USD, JPY)")


class DayPlan(BaseModel):
    day: int = Field(description="Day number (e.g., 1, 2, 3)")
    theme: str = Field(description="Theme of the day (e.g., 'Art and Culture')")
    activities: List[ActivityDetail] = Field(
        description="List of activities for the day"
    )


class FinalItinerary(BaseModel):
    destination: str = Field(description="Destination city or country")
    weather_summary: str = Field(description="Weather summary and clothing advice")
    daily_plans: List[DayPlan] = Field(description="Detailed day-by-day schedule")
    total_estimated_budget: float = Field(
        description="Calculated approximate total budget"
    )
    currency: str = Field(description="Reference currency")

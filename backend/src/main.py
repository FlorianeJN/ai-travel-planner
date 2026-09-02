from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.travel import router

app = FastAPI(title="AI Travel Planner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1/travel")

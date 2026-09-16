from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import groups, workouts, leaderboard

app = FastAPI(title="Gym Leaderboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groups.router)
app.include_router(workouts.router)
app.include_router(leaderboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}

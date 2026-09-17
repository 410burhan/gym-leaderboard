from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import profiles, follows, workouts, feed, posts, likes, comments

app = FastAPI(title="Gym Social API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(follows.router)
app.include_router(workouts.router)
app.include_router(feed.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)


@app.get("/health")
def health():
    return {"status": "ok"}

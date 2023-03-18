from fastapi import FastAPI

from .routers import posts, users
from app.database import create_db_and_tables

app = FastAPI(
    title="secretely-api",
    version="0.0.2"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(users.router)
app.include_router(posts.router)
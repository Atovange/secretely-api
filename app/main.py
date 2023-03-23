from fastapi import FastAPI
from fastapi import __version__ as fastapi_version

from app.routers import posts, users
from app.database import create_db_and_tables, DBSession
from app.crud import authenticate_user

app = FastAPI(
    title="secretely-api",
    version="0.0.3"
)

print("fastapi version: " + fastapi_version)
# print(authenticate_user(DBSession, email="johndoe@gmail.com", password="secret"))

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(users.router)
app.include_router(posts.router)
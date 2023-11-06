from fastapi import FastAPI

from fastapi_sqlmodel.db.db import init_db
from fastapi_sqlmodel.routers.example import router as example_router

app = FastAPI()

app.include_router(
    example_router,
    tags=["example"],
    prefix="/example"
)

@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
def read_root():
    return {"Hello": "World"}

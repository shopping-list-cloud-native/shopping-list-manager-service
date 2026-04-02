from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.lists import router as lists_router

app = FastAPI(title="List Manager Service")

app.include_router(health_router)
app.include_router(lists_router)

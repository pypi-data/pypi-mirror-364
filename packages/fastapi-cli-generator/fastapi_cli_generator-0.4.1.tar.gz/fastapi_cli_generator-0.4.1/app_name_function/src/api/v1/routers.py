from fastapi import APIRouter

from .endpoints.items import items_router


all_routers = APIRouter()
all_routers.include_router(items_router, prefix="/items")
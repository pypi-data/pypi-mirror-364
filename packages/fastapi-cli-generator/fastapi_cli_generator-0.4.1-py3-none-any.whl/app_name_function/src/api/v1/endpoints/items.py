from fastapi import APIRouter


items_router = APIRouter()


@items_router.get("/")
async def read_items():
    return {"message": "Hello Items!"}

from fastapi import APIRouter, Depends

from fastapi_sqlmodel.models.example import SongCreate
from fastapi_sqlmodel.services.example import ExampleService, get_example_service

router = APIRouter()

@router.post("/songs")
async def add_song(
    request: SongCreate,
    example_service: ExampleService = Depends(get_example_service),
):
    return await example_service.create(**request.dict())

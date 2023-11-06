from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends

from fastapi_sqlmodel.db.db import get_session
from fastapi_sqlmodel.models.example import Song
from fastapi_sqlmodel.db.db import get_session


class ExampleService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(
        self,
        name: str,
        artist: str,
    ) -> Song:
        song = Song(name=name, artist=artist)
        self.db_session.add(song)
        await self.db_session.commit()
        await self.db_session.refresh(song)
        return song


async def get_example_service(session: AsyncSession = Depends(get_session)):
    yield ExampleService(session)

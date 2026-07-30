from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.entities import School
from app.repositories.base import BaseRepository


class SchoolRepository(BaseRepository[School]):
    def __init__(self, session: Session):
        super().__init__(School, session)

    def get_by_slug(self, slug: str) -> Optional[School]:
        stmt = select(School).where(School.slug == slug)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_name(self, name: str) -> Optional[School]:
        stmt = select(School).where(School.name == name)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

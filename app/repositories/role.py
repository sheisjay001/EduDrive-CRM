from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.entities import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: Session):
        super().__init__(Role, session)

    def get_by_school(self, school_id: str) -> List[Role]:
        stmt = select(Role).where(Role.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_name(self, school_id: str, name: str) -> Optional[Role]:
        stmt = select(Role).where(
            Role.school_id == school_id,
            Role.name == name
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

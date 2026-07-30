from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.entities import Parent
from app.repositories.base import BaseRepository


class ParentRepository(BaseRepository[Parent]):
    def __init__(self, session: Session):
        super().__init__(Parent, session)

    def get_by_school(self, school_id: str) -> List[Parent]:
        stmt = select(Parent).where(Parent.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_family(self, family_id: str) -> List[Parent]:
        stmt = select(Parent).where(Parent.family_id == family_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_email(self, school_id: str, email: str) -> Optional[Parent]:
        stmt = select(Parent).where(
            Parent.school_id == school_id,
            Parent.email == email
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_phone(self, school_id: str, phone: str) -> Optional[Parent]:
        stmt = select(Parent).where(
            Parent.school_id == school_id,
            Parent.phone == phone
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

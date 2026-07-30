from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.entities import Family
from app.repositories.base import BaseRepository


class FamilyRepository(BaseRepository[Family]):
    def __init__(self, session: Session):
        super().__init__(Family, session)

    def get_by_school(self, school_id: str) -> List[Family]:
        stmt = select(Family).where(Family.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_household_name(self, school_id: str, household_name: str) -> Optional[Family]:
        stmt = select(Family).where(
            Family.school_id == school_id,
            Family.household_name == household_name
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

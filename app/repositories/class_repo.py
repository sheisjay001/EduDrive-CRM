from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.entities import Class as ClassModel
from app.repositories.base import BaseRepository


class ClassRepository(BaseRepository[ClassModel]):
    def __init__(self, session: Session):
        super().__init__(ClassModel, session)

    def get_by_school(self, school_id: str) -> List[ClassModel]:
        stmt = select(ClassModel).where(ClassModel.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_name(self, school_id: str, name: str) -> Optional[ClassModel]:
        stmt = select(ClassModel).where(
            ClassModel.school_id == school_id,
            ClassModel.name == name
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_level(self, school_id: str, level_group: str) -> List[ClassModel]:
        stmt = select(ClassModel).where(
            ClassModel.school_id == school_id,
            ClassModel.level_group == level_group
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.entities import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, session: Session):
        super().__init__(Student, session)

    def get_by_school(self, school_id: str) -> List[Student]:
        stmt = select(Student).where(Student.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_family(self, family_id: str) -> List[Student]:
        stmt = select(Student).where(Student.family_id == family_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_class(self, class_id: str) -> List[Student]:
        stmt = select(Student).where(Student.class_id == class_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_admission_no(self, school_id: str, admission_no: str) -> Optional[Student]:
        stmt = select(Student).where(
            Student.school_id == school_id,
            Student.admission_no == admission_no
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_lead(self, lead_id: str) -> Optional[Student]:
        stmt = select(Student).where(Student.lead_id == lead_id)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

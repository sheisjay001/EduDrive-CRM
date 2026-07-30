from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.entities import Lead
from app.repositories.base import BaseRepository


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, session: Session):
        super().__init__(Lead, session)

    def get_by_school(self, school_id: str) -> List[Lead]:
        stmt = select(Lead).where(Lead.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_stage(self, school_id: str, stage: str) -> List[Lead]:
        stmt = select(Lead).where(
            Lead.school_id == school_id,
            Lead.stage == stage
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_source(self, school_id: str, source: str) -> List[Lead]:
        stmt = select(Lead).where(
            Lead.school_id == school_id,
            Lead.source == source
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_follow_ups(self, school_id: str) -> List[Lead]:
        from datetime import datetime
        stmt = select(Lead).where(
            Lead.school_id == school_id,
            Lead.follow_up_at <= datetime.utcnow()
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

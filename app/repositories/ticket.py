from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.entities import Ticket
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, session: Session):
        super().__init__(Ticket, session)

    def get_by_school(self, school_id: str) -> List[Ticket]:
        stmt = select(Ticket).where(Ticket.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_status(self, school_id: str, status: str) -> List[Ticket]:
        stmt = select(Ticket).where(
            Ticket.school_id == school_id,
            Ticket.status == status
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_parent(self, parent_id: str) -> List[Ticket]:
        stmt = select(Ticket).where(Ticket.parent_id == parent_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_family(self, family_id: str) -> List[Ticket]:
        stmt = select(Ticket).where(Ticket.family_id == family_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_assignee(self, assignee_user_id: str) -> List[Ticket]:
        stmt = select(Ticket).where(Ticket.assignee_user_id == assignee_user_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_overdue_sla(self, school_id: str) -> List[Ticket]:
        from datetime import datetime
        stmt = select(Ticket).where(
            Ticket.school_id == school_id,
            Ticket.sla_due_at < datetime.utcnow(),
            Ticket.status.in_(["open", "assigned", "in_progress"])
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

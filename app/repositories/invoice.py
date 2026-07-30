from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.models.entities import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: Session):
        super().__init__(Invoice, session)

    def get_by_school(self, school_id: str) -> List[Invoice]:
        stmt = select(Invoice).where(Invoice.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_student(self, student_id: str) -> List[Invoice]:
        stmt = select(Invoice).where(Invoice.student_id == student_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_status(self, school_id: str, status: str) -> List[Invoice]:
        stmt = select(Invoice).where(
            Invoice.school_id == school_id,
            Invoice.status == status
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_invoice_number(self, school_id: str, invoice_number: str) -> Optional[Invoice]:
        stmt = select(Invoice).where(
            Invoice.school_id == school_id,
            Invoice.invoice_number == invoice_number
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_overdue(self, school_id: str) -> List[Invoice]:
        from datetime import datetime, date
        stmt = select(Invoice).where(
            Invoice.school_id == school_id,
            Invoice.status == "issued",
            Invoice.due_date < date.today()
        )
        result = self.session.execute(stmt)
        return list(result.scalars().all())

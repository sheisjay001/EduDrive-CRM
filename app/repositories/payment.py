from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.entities import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: Session):
        super().__init__(Payment, session)

    def get_by_school(self, school_id: str) -> List[Payment]:
        stmt = select(Payment).where(Payment.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_invoice(self, invoice_id: str) -> List[Payment]:
        stmt = select(Payment).where(Payment.invoice_id == invoice_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def get_by_provider_reference(self, school_id: str, reference: str) -> Optional[Payment]:
        stmt = select(Payment).where(
            Payment.school_id == school_id,
            Payment.provider_reference == reference
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_total_for_invoice(self, invoice_id: str) -> float:
        from sqlalchemy import func
        stmt = select(func.sum(Payment.amount)).where(Payment.invoice_id == invoice_id)
        result = self.session.execute(stmt)
        return result.scalar() or 0.0

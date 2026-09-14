from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import Payment
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: Session):
        super().__init__(Payment, session)

    def get_by_school(self, school_id: str, pagination: Optional[PaginationParams] = None) -> List[Payment] | PaginatedResult:
        """Get payments by school with optional pagination"""
        try:
            stmt = select(Payment).where(Payment.school_id == school_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Payment).where(Payment.school_id == school_id)
                total_result = self.session.execute(total_stmt)
                total = total_result.scalar()
                
                stmt = stmt.offset(pagination.skip).limit(pagination.limit)
                result = self.session.execute(stmt)
                items = list(result.scalars().all())
                return PaginatedResult(items, total, pagination.skip, pagination.limit)
            else:
                result = self.session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            import logging
            logging.error(f"Error fetching payments by school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_invoice(self, invoice_id: str, pagination: Optional[PaginationParams] = None) -> List[Payment] | PaginatedResult:
        """Get payments by invoice with optional pagination"""
        try:
            stmt = select(Payment).where(Payment.invoice_id == invoice_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Payment).where(Payment.invoice_id == invoice_id)
                total_result = self.session.execute(total_stmt)
                total = total_result.scalar()
                
                stmt = stmt.offset(pagination.skip).limit(pagination.limit)
                result = self.session.execute(stmt)
                items = list(result.scalars().all())
                return PaginatedResult(items, total, pagination.skip, pagination.limit)
            else:
                result = self.session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            import logging
            logging.error(f"Error fetching payments by invoice {invoice_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_provider_reference(self, school_id: str, reference: str) -> Optional[Payment]:
        """Get payment by provider reference within a school"""
        try:
            stmt = select(Payment).where(
                Payment.school_id == school_id,
                Payment.provider_reference == reference
            )
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching payment by reference {reference}: {e}")
            return None

    def get_total_for_invoice(self, invoice_id: str) -> float:
        """Get total payment amount for an invoice"""
        try:
            from sqlalchemy import func
            stmt = select(func.sum(Payment.amount)).where(Payment.invoice_id == invoice_id)
            result = self.session.execute(stmt)
            return result.scalar() or 0.0
        except Exception as e:
            import logging
            logging.error(f"Error calculating total for invoice {invoice_id}: {e}")
            return 0.0

    def get_by_date_range(self, school_id: str, start_date: str, end_date: str, pagination: Optional[PaginationParams] = None) -> List[Payment] | PaginatedResult:
        """Get payments within a date range"""
        try:
            stmt = select(Payment).where(
                Payment.school_id == school_id,
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Payment).where(
                    Payment.school_id == school_id,
                    Payment.payment_date >= start_date,
                    Payment.payment_date <= end_date
                )
                total_result = self.session.execute(total_stmt)
                total = total_result.scalar()
                
                stmt = stmt.offset(pagination.skip).limit(pagination.limit)
                result = self.session.execute(stmt)
                items = list(result.scalars().all())
                return PaginatedResult(items, total, pagination.skip, pagination.limit)
            else:
                result = self.session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            import logging
            logging.error(f"Error fetching payments by date range: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_total_for_school(self, school_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> float:
        """Get total payment amount for a school with optional date range"""
        try:
            from sqlalchemy import func
            stmt = select(func.sum(Payment.amount)).where(Payment.school_id == school_id)
            
            if start_date:
                stmt = stmt.where(Payment.payment_date >= start_date)
            if end_date:
                stmt = stmt.where(Payment.payment_date <= end_date)
            
            result = self.session.execute(stmt)
            return result.scalar() or 0.0
        except Exception as e:
            import logging
            logging.error(f"Error calculating total for school {school_id}: {e}")
            return 0.0

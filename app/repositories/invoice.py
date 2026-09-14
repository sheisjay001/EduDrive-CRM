from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import Invoice
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: Session):
        super().__init__(Invoice, session)

    def get_by_school(self, school_id: str, pagination: Optional[PaginationParams] = None, status: Optional[str] = None) -> List[Invoice] | PaginatedResult:
        """Get invoices by school with optional pagination and status filter"""
        try:
            stmt = select(Invoice).where(Invoice.school_id == school_id)
            if status:
                stmt = stmt.where(Invoice.status == status)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Invoice).where(Invoice.school_id == school_id)
                if status:
                    total_stmt = total_stmt.where(Invoice.status == status)
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
            logging.error(f"Error fetching invoices by school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_student(self, student_id: str, pagination: Optional[PaginationParams] = None) -> List[Invoice] | PaginatedResult:
        """Get invoices by student with optional pagination"""
        try:
            stmt = select(Invoice).where(Invoice.student_id == student_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Invoice).where(Invoice.student_id == student_id)
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
            logging.error(f"Error fetching invoices by student {student_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_status(self, school_id: str, status: str, pagination: Optional[PaginationParams] = None) -> List[Invoice] | PaginatedResult:
        """Get invoices by status within a school with optional pagination"""
        try:
            stmt = select(Invoice).where(
                Invoice.school_id == school_id,
                Invoice.status == status
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Invoice).where(
                    Invoice.school_id == school_id,
                    Invoice.status == status
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
            logging.error(f"Error fetching invoices by status {status}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_invoice_number(self, school_id: str, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number within a school"""
        try:
            stmt = select(Invoice).where(
                Invoice.school_id == school_id,
                Invoice.invoice_number == invoice_number
            )
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching invoice by number {invoice_number}: {e}")
            return None

    def get_overdue(self, school_id: str, pagination: Optional[PaginationParams] = None) -> List[Invoice] | PaginatedResult:
        """Get overdue invoices within a school with optional pagination"""
        try:
            from datetime import datetime, date
            stmt = select(Invoice).where(
                Invoice.school_id == school_id,
                Invoice.status == "issued",
                Invoice.due_date < date.today()
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Invoice).where(
                    Invoice.school_id == school_id,
                    Invoice.status == "issued",
                    Invoice.due_date < date.today()
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
            logging.error(f"Error fetching overdue invoices for school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_due_soon(self, school_id: str, days: int = 7, pagination: Optional[PaginationParams] = None) -> List[Invoice] | PaginatedResult:
        """Get invoices due within specified days"""
        try:
            from datetime import datetime, date, timedelta
            due_date = date.today() + timedelta(days=days)
            stmt = select(Invoice).where(
                Invoice.school_id == school_id,
                Invoice.status == "issued",
                Invoice.due_date <= due_date,
                Invoice.due_date >= date.today()
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Invoice).where(
                    Invoice.school_id == school_id,
                    Invoice.status == "issued",
                    Invoice.due_date <= due_date,
                    Invoice.due_date >= date.today()
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
            logging.error(f"Error fetching invoices due soon for school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_total_outstanding(self, school_id: str) -> float:
        """Get total outstanding amount for a school"""
        try:
            from sqlalchemy import func
            stmt = select(func.sum(Invoice.amount_due - Invoice.amount_paid)).where(
                Invoice.school_id == school_id,
                Invoice.status.in_("issued", "partially_paid")
            )
            result = self.session.execute(stmt)
            return result.scalar() or 0.0
        except Exception as e:
            import logging
            logging.error(f"Error calculating total outstanding for school {school_id}: {e}")
            return 0.0

    def bulk_update_status(self, invoice_ids: List[str], new_status: str) -> int:
        """Bulk update status for multiple invoices"""
        try:
            from sqlalchemy import update
            stmt = update(Invoice).where(Invoice.id.in_(invoice_ids)).values(status=new_status)
            result = self.session.execute(stmt)
            self.session.commit()
            return result.rowcount
        except Exception as e:
            self.session.rollback()
            import logging
            logging.error(f"Error bulk updating invoice statuses: {e}")
            raise

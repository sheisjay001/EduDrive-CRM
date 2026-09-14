from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import Ticket
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, session: Session):
        super().__init__(Ticket, session)

    def get_by_school(self, school_id: str, pagination: Optional[PaginationParams] = None, status: Optional[str] = None) -> List[Ticket] | PaginatedResult:
        """Get tickets by school with optional pagination and status filter"""
        try:
            stmt = select(Ticket).where(Ticket.school_id == school_id)
            if status:
                stmt = stmt.where(Ticket.status == status)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Ticket).where(Ticket.school_id == school_id)
                if status:
                    total_stmt = total_stmt.where(Ticket.status == status)
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
            logging.error(f"Error fetching tickets by school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_status(self, school_id: str, status: str, pagination: Optional[PaginationParams] = None) -> List[Ticket] | PaginatedResult:
        """Get tickets by status within a school with optional pagination"""
        try:
            stmt = select(Ticket).where(
                Ticket.school_id == school_id,
                Ticket.status == status
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Ticket).where(
                    Ticket.school_id == school_id,
                    Ticket.status == status
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
            logging.error(f"Error fetching tickets by status {status}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_parent(self, parent_id: str, pagination: Optional[PaginationParams] = None) -> List[Ticket] | PaginatedResult:
        """Get tickets by parent with optional pagination"""
        try:
            stmt = select(Ticket).where(Ticket.parent_id == parent_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Ticket).where(Ticket.parent_id == parent_id)
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
            logging.error(f"Error fetching tickets by parent {parent_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_family(self, family_id: str, pagination: Optional[PaginationParams] = None) -> List[Ticket] | PaginatedResult:
        """Get tickets by family with optional pagination"""
        try:
            stmt = select(Ticket).where(Ticket.family_id == family_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Ticket).where(Ticket.family_id == family_id)
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
            logging.error(f"Error fetching tickets by family {family_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_assignee(self, assignee_user_id: str, pagination: Optional[PaginationParams] = None) -> List[Ticket] | PaginatedResult:
        """Get tickets by assignee with optional pagination"""
        try:
            stmt = select(Ticket).where(Ticket.assignee_user_id == assignee_user_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Ticket).where(Ticket.assignee_user_id == assignee_user_id)
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
            logging.error(f"Error fetching tickets by assignee {assignee_user_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_overdue_sla(self, school_id: str, pagination: Optional[PaginationParams] = None) -> List[Ticket] | PaginatedResult:
        """Get tickets with overdue SLA within a school with optional pagination"""
        try:
            from datetime import datetime
            stmt = select(Ticket).where(
                Ticket.school_id == school_id,
                Ticket.sla_due_at < datetime.utcnow(),
                Ticket.status.in_("open", "assigned", "in_progress")
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Ticket).where(
                    Ticket.school_id == school_id,
                    Ticket.sla_due_at < datetime.utcnow(),
                    Ticket.status.in_("open", "assigned", "in_progress")
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
            logging.error(f"Error fetching overdue SLA tickets for school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def search_tickets(self, school_id: str, search_term: str, pagination: Optional[PaginationParams] = None) -> List[Ticket] | PaginatedResult:
        """Search tickets by subject or description"""
        try:
            search_pattern = f"%{search_term}%"
            stmt = select(Ticket).where(
                Ticket.school_id == school_id,
                or_(
                    Ticket.subject.ilike(search_pattern),
                    Ticket.description.ilike(search_pattern)
                )
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Ticket).where(
                    Ticket.school_id == school_id,
                    or_(
                        Ticket.subject.ilike(search_pattern),
                        Ticket.description.ilike(search_pattern)
                    )
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
            logging.error(f"Error searching tickets with term {search_term}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_priority(self, school_id: str, priority: str, pagination: Optional[PaginationParams] = None) -> List[Ticket] | PaginatedResult:
        """Get tickets by priority within a school with optional pagination"""
        try:
            stmt = select(Ticket).where(
                Ticket.school_id == school_id,
                Ticket.priority == priority
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Ticket).where(
                    Ticket.school_id == school_id,
                    Ticket.priority == priority
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
            logging.error(f"Error fetching tickets by priority {priority}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_open_count(self, school_id: str) -> int:
        """Get count of open tickets in a school"""
        try:
            from sqlalchemy import func
            stmt = select(func.count()).select_from(Ticket).where(
                Ticket.school_id == school_id,
                Ticket.status.in_("open", "assigned", "in_progress")
            )
            result = self.session.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            import logging
            logging.error(f"Error counting open tickets for school {school_id}: {e}")
            return 0

    def bulk_update_status(self, ticket_ids: List[str], new_status: str) -> int:
        """Bulk update status for multiple tickets"""
        try:
            from sqlalchemy import update
            stmt = update(Ticket).where(Ticket.id.in_(ticket_ids)).values(status=new_status)
            result = self.session.execute(stmt)
            self.session.commit()
            return result.rowcount
        except Exception as e:
            self.session.rollback()
            import logging
            logging.error(f"Error bulk updating ticket statuses: {e}")
            raise

    def bulk_assign(self, ticket_ids: List[str], assignee_user_id: str) -> int:
        """Bulk assign tickets to a user"""
        try:
            from sqlalchemy import update
            from datetime import datetime
            stmt = update(Ticket).where(Ticket.id.in_(ticket_ids)).values(
                assignee_user_id=assignee_user_id,
                status="assigned",
                assigned_at=datetime.utcnow()
            )
            result = self.session.execute(stmt)
            self.session.commit()
            return result.rowcount
        except Exception as e:
            self.session.rollback()
            import logging
            logging.error(f"Error bulk assigning tickets: {e}")
            raise

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import Lead
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, session: Session):
        super().__init__(Lead, session)

    def get_by_school(self, school_id: str, pagination: Optional[PaginationParams] = None, stage: Optional[str] = None) -> List[Lead] | PaginatedResult:
        """Get leads by school with optional pagination and stage filter"""
        try:
            stmt = select(Lead).where(Lead.school_id == school_id)
            if stage:
                stmt = stmt.where(Lead.stage == stage)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Lead).where(Lead.school_id == school_id)
                if stage:
                    total_stmt = total_stmt.where(Lead.stage == stage)
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
            logging.error(f"Error fetching leads by school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_stage(self, school_id: str, stage: str, pagination: Optional[PaginationParams] = None) -> List[Lead] | PaginatedResult:
        """Get leads by stage within a school with optional pagination"""
        try:
            stmt = select(Lead).where(
                Lead.school_id == school_id,
                Lead.stage == stage
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Lead).where(
                    Lead.school_id == school_id,
                    Lead.stage == stage
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
            logging.error(f"Error fetching leads by stage {stage}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_source(self, school_id: str, source: str, pagination: Optional[PaginationParams] = None) -> List[Lead] | PaginatedResult:
        """Get leads by source within a school with optional pagination"""
        try:
            stmt = select(Lead).where(
                Lead.school_id == school_id,
                Lead.source == source
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Lead).where(
                    Lead.school_id == school_id,
                    Lead.source == source
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
            logging.error(f"Error fetching leads by source {source}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_follow_ups(self, school_id: str, pagination: Optional[PaginationParams] = None) -> List[Lead] | PaginatedResult:
        """Get leads that need follow-up (follow_up_at has passed) with optional pagination"""
        try:
            from datetime import datetime
            stmt = select(Lead).where(
                Lead.school_id == school_id,
                Lead.follow_up_at <= datetime.utcnow()
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Lead).where(
                    Lead.school_id == school_id,
                    Lead.follow_up_at <= datetime.utcnow()
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
            logging.error(f"Error fetching follow-up leads for school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def search_leads(self, school_id: str, search_term: str, pagination: Optional[PaginationParams] = None) -> List[Lead] | PaginatedResult:
        """Search leads by child name or parent name"""
        try:
            search_pattern = f"%{search_term}%"
            stmt = select(Lead).where(
                Lead.school_id == school_id,
                or_(
                    Lead.child_name.ilike(search_pattern),
                    Lead.parent_name.ilike(search_pattern)
                )
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Lead).where(
                    Lead.school_id == school_id,
                    or_(
                        Lead.child_name.ilike(search_pattern),
                        Lead.parent_name.ilike(search_pattern)
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
            logging.error(f"Error searching leads with term {search_term}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_conversion_rate(self, school_id: str) -> float:
        """Calculate lead conversion rate for a school"""
        try:
            from sqlalchemy import func
            total_stmt = select(func.count()).select_from(Lead).where(Lead.school_id == school_id)
            total_result = self.session.execute(total_stmt)
            total = total_result.scalar() or 0
            
            if total == 0:
                return 0.0
            
            converted_stmt = select(func.count()).select_from(Lead).where(
                Lead.school_id == school_id,
                Lead.stage == "enrolled"
            )
            converted_result = self.session.execute(converted_stmt)
            converted = converted_result.scalar() or 0
            
            return (converted / total) * 100
        except Exception as e:
            import logging
            logging.error(f"Error calculating conversion rate for school {school_id}: {e}")
            return 0.0

    def bulk_update_stage(self, lead_ids: List[str], new_stage: str) -> int:
        """Bulk update stage for multiple leads"""
        try:
            from sqlalchemy import update
            stmt = update(Lead).where(Lead.id.in_(lead_ids)).values(stage=new_stage)
            result = self.session.execute(stmt)
            self.session.commit()
            return result.rowcount
        except Exception as e:
            self.session.rollback()
            import logging
            logging.error(f"Error bulk updating lead stages: {e}")
            raise

    def get_stale_leads(self, school_id: str, days: int = 30, pagination: Optional[PaginationParams] = None) -> List[Lead] | PaginatedResult:
        """Get leads that haven't been updated in specified days"""
        try:
            from datetime import datetime, timedelta
            stale_date = datetime.utcnow() - timedelta(days=days)
            stmt = select(Lead).where(
                Lead.school_id == school_id,
                Lead.updated_at < stale_date,
                Lead.stage != "enrolled"
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Lead).where(
                    Lead.school_id == school_id,
                    Lead.updated_at < stale_date,
                    Lead.stage != "enrolled"
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
            logging.error(f"Error fetching stale leads for school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

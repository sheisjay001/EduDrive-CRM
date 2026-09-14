from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import School
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class SchoolRepository(BaseRepository[School]):
    def __init__(self, session: Session):
        super().__init__(School, session)

    def get_by_slug(self, slug: str) -> Optional[School]:
        """Get school by slug"""
        try:
            stmt = select(School).where(School.slug == slug)
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching school by slug {slug}: {e}")
            return None

    def get_by_name(self, name: str) -> Optional[School]:
        """Get school by name"""
        try:
            stmt = select(School).where(School.name == name)
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching school by name {name}: {e}")
            return None

    def search_schools(self, search_term: str, pagination: Optional[PaginationParams] = None) -> List[School] | PaginatedResult:
        """Search schools by name"""
        try:
            search_pattern = f"%{search_term}%"
            stmt = select(School).where(School.name.ilike(search_pattern))
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(School).where(School.name.ilike(search_pattern))
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
            logging.error(f"Error searching schools with term {search_term}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_active_schools(self, pagination: Optional[PaginationParams] = None) -> List[School] | PaginatedResult:
        """Get all active schools"""
        try:
            stmt = select(School).where(School.is_active == True)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(School).where(School.is_active == True)
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
            logging.error(f"Error fetching active schools: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

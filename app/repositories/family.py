from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import Family
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class FamilyRepository(BaseRepository[Family]):
    def __init__(self, session: Session):
        super().__init__(Family, session)

    def get_by_school(self, school_id: str, pagination: Optional[PaginationParams] = None) -> List[Family] | PaginatedResult:
        """Get families by school with optional pagination"""
        try:
            stmt = select(Family).where(Family.school_id == school_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Family).where(Family.school_id == school_id)
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
            logging.error(f"Error fetching families by school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_household_name(self, school_id: str, household_name: str) -> Optional[Family]:
        """Get family by household name within a school"""
        try:
            stmt = select(Family).where(
                Family.school_id == school_id,
                Family.household_name == household_name
            )
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching family by household name {household_name}: {e}")
            return None

    def search_families(self, school_id: str, search_term: str, pagination: Optional[PaginationParams] = None) -> List[Family] | PaginatedResult:
        """Search families by household name"""
        try:
            search_pattern = f"%{search_term}%"
            stmt = select(Family).where(
                Family.school_id == school_id,
                Family.household_name.ilike(search_pattern)
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Family).where(
                    Family.school_id == school_id,
                    Family.household_name.ilike(search_pattern)
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
            logging.error(f"Error searching families with term {search_term}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

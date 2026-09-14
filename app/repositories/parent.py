from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import Parent
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class ParentRepository(BaseRepository[Parent]):
    def __init__(self, session: Session):
        super().__init__(Parent, session)

    def get_by_school(self, school_id: str, pagination: Optional[PaginationParams] = None) -> List[Parent] | PaginatedResult:
        """Get parents by school with optional pagination"""
        try:
            stmt = select(Parent).where(Parent.school_id == school_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Parent).where(Parent.school_id == school_id)
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
            logging.error(f"Error fetching parents by school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_family(self, family_id: str, pagination: Optional[PaginationParams] = None) -> List[Parent] | PaginatedResult:
        """Get parents by family with optional pagination"""
        try:
            stmt = select(Parent).where(Parent.family_id == family_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Parent).where(Parent.family_id == family_id)
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
            logging.error(f"Error fetching parents by family {family_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_email(self, school_id: str, email: str) -> Optional[Parent]:
        """Get parent by email within a school"""
        try:
            stmt = select(Parent).where(
                Parent.school_id == school_id,
                Parent.email == email
            )
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching parent by email {email}: {e}")
            return None

    def get_by_phone(self, school_id: str, phone: str) -> Optional[Parent]:
        """Get parent by phone within a school"""
        try:
            stmt = select(Parent).where(
                Parent.school_id == school_id,
                Parent.phone == phone
            )
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching parent by phone {phone}: {e}")
            return None

    def search_parents(self, school_id: str, search_term: str, pagination: Optional[PaginationParams] = None) -> List[Parent] | PaginatedResult:
        """Search parents by name or email"""
        try:
            search_pattern = f"%{search_term}%"
            stmt = select(Parent).where(
                Parent.school_id == school_id,
                or_(
                    Parent.first_name.ilike(search_pattern),
                    Parent.last_name.ilike(search_pattern),
                    Parent.email.ilike(search_pattern)
                )
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Parent).where(
                    Parent.school_id == school_id,
                    or_(
                        Parent.first_name.ilike(search_pattern),
                        Parent.last_name.ilike(search_pattern),
                        Parent.email.ilike(search_pattern)
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
            logging.error(f"Error searching parents with term {search_term}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import Class as ClassModel
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class ClassRepository(BaseRepository[ClassModel]):
    def __init__(self, session: Session):
        super().__init__(ClassModel, session)

    def get_by_school(self, school_id: str, pagination: Optional[PaginationParams] = None) -> List[ClassModel] | PaginatedResult:
        """Get classes by school with optional pagination"""
        try:
            stmt = select(ClassModel).where(ClassModel.school_id == school_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(ClassModel).where(ClassModel.school_id == school_id)
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
            logging.error(f"Error fetching classes by school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_name(self, school_id: str, name: str) -> Optional[ClassModel]:
        """Get class by name within a school"""
        try:
            stmt = select(ClassModel).where(
                ClassModel.school_id == school_id,
                ClassModel.name == name
            )
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching class by name {name}: {e}")
            return None

    def get_by_level(self, school_id: str, level_group: str, pagination: Optional[PaginationParams] = None) -> List[ClassModel] | PaginatedResult:
        """Get classes by level group within a school with optional pagination"""
        try:
            stmt = select(ClassModel).where(
                ClassModel.school_id == school_id,
                ClassModel.level_group == level_group
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(ClassModel).where(
                    ClassModel.school_id == school_id,
                    ClassModel.level_group == level_group
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
            logging.error(f"Error fetching classes by level {level_group}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def search_classes(self, school_id: str, search_term: str, pagination: Optional[PaginationParams] = None) -> List[ClassModel] | PaginatedResult:
        """Search classes by name"""
        try:
            search_pattern = f"%{search_term}%"
            stmt = select(ClassModel).where(
                ClassModel.school_id == school_id,
                ClassModel.name.ilike(search_pattern)
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(ClassModel).where(
                    ClassModel.school_id == school_id,
                    ClassModel.name.ilike(search_pattern)
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
            logging.error(f"Error searching classes with term {search_term}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

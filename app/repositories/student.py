from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import Student
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class StudentRepository(BaseRepository[Student]):
    def __init__(self, session: Session):
        super().__init__(Student, session)

    def get_by_school(self, school_id: str, pagination: Optional[PaginationParams] = None, status: Optional[str] = None) -> List[Student] | PaginatedResult:
        """Get students by school with optional pagination and status filter"""
        try:
            stmt = select(Student).where(Student.school_id == school_id)
            if status:
                stmt = stmt.where(Student.status == status)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Student).where(Student.school_id == school_id)
                if status:
                    total_stmt = total_stmt.where(Student.status == status)
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
            logging.error(f"Error fetching students by school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_family(self, family_id: str, pagination: Optional[PaginationParams] = None) -> List[Student] | PaginatedResult:
        """Get students by family with optional pagination"""
        try:
            stmt = select(Student).where(Student.family_id == family_id)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Student).where(Student.family_id == family_id)
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
            logging.error(f"Error fetching students by family {family_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_class(self, class_id: str, pagination: Optional[PaginationParams] = None, status: Optional[str] = None) -> List[Student] | PaginatedResult:
        """Get students by class with optional pagination and status filter"""
        try:
            stmt = select(Student).where(Student.class_id == class_id)
            if status:
                stmt = stmt.where(Student.status == status)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Student).where(Student.class_id == class_id)
                if status:
                    total_stmt = total_stmt.where(Student.status == status)
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
            logging.error(f"Error fetching students by class {class_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_by_admission_no(self, school_id: str, admission_no: str) -> Optional[Student]:
        """Get student by admission number within a school"""
        try:
            stmt = select(Student).where(
                Student.school_id == school_id,
                Student.admission_no == admission_no
            )
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching student by admission no {admission_no}: {e}")
            return None

    def get_by_lead(self, lead_id: str) -> Optional[Student]:
        """Get student converted from a lead"""
        try:
            stmt = select(Student).where(Student.lead_id == lead_id)
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching student by lead {lead_id}: {e}")
            return None

    def search_students(self, school_id: str, search_term: str, pagination: Optional[PaginationParams] = None) -> List[Student] | PaginatedResult:
        """Search students by name or admission number"""
        try:
            search_pattern = f"%{search_term}%"
            stmt = select(Student).where(
                Student.school_id == school_id,
                or_(
                    Student.first_name.ilike(search_pattern),
                    Student.last_name.ilike(search_pattern),
                    Student.admission_no.ilike(search_pattern)
                )
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(Student).where(
                    Student.school_id == school_id,
                    or_(
                        Student.first_name.ilike(search_pattern),
                        Student.last_name.ilike(search_pattern),
                        Student.admission_no.ilike(search_pattern)
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
            logging.error(f"Error searching students with term {search_term}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_active_count(self, school_id: str) -> int:
        """Get count of active students in a school"""
        try:
            from sqlalchemy import func
            stmt = select(func.count()).select_from(Student).where(
                Student.school_id == school_id,
                Student.status == 'active'
            )
            result = self.session.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            import logging
            logging.error(f"Error counting active students for school {school_id}: {e}")
            return 0

    def bulk_update_class(self, student_ids: List[str], new_class_id: str) -> int:
        """Bulk update class for multiple students"""
        try:
            from sqlalchemy import update
            stmt = update(Student).where(Student.id.in_(student_ids)).values(class_id=new_class_id)
            result = self.session.execute(stmt)
            self.session.commit()
            return result.rowcount
        except Exception as e:
            self.session.rollback()
            import logging
            logging.error(f"Error bulk updating student classes: {e}")
            raise

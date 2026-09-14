from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from app.models.entities import User
from app.repositories.base import BaseRepository, PaginationParams, PaginatedResult


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str, school_id: str) -> Optional[User]:
        """Get user by email within a school"""
        try:
            stmt = select(User).where(
                User.email == email,
                User.school_id == school_id
            )
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            import logging
            logging.error(f"Error fetching user by email {email}: {e}")
            return None

    def get_by_school(self, school_id: str, pagination: Optional[PaginationParams] = None, role: Optional[str] = None) -> List[User] | PaginatedResult:
        """Get users by school with optional pagination and role filter"""
        try:
            stmt = select(User).where(User.school_id == school_id)
            if role:
                stmt = stmt.where(User.role == role)
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(User).where(User.school_id == school_id)
                if role:
                    total_stmt = total_stmt.where(User.role == role)
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
            logging.error(f"Error fetching users by school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def update_last_login(self, user: User) -> User:
        """Update user's last login timestamp"""
        from datetime import datetime
        return self.update(user, last_login_at=datetime.utcnow())

    def get_by_role(self, school_id: str, role: str, pagination: Optional[PaginationParams] = None) -> List[User] | PaginatedResult:
        """Get users by specific role within a school"""
        try:
            stmt = select(User).where(
                User.school_id == school_id,
                User.role == role
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(User).where(
                    User.school_id == school_id,
                    User.role == role
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
            logging.error(f"Error fetching users by role {role}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def search_users(self, school_id: str, search_term: str, pagination: Optional[PaginationParams] = None) -> List[User] | PaginatedResult:
        """Search users by name or email"""
        try:
            search_pattern = f"%{search_term}%"
            stmt = select(User).where(
                User.school_id == school_id,
                or_(
                    User.first_name.ilike(search_pattern),
                    User.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern)
                )
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(User).where(
                    User.school_id == school_id,
                    or_(
                        User.first_name.ilike(search_pattern),
                        User.last_name.ilike(search_pattern),
                        User.email.ilike(search_pattern)
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
            logging.error(f"Error searching users with term {search_term}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def get_active_users(self, school_id: str, pagination: Optional[PaginationParams] = None) -> List[User] | PaginatedResult:
        """Get active users (users who have logged in recently)"""
        try:
            from datetime import datetime, timedelta
            recent_date = datetime.utcnow() - timedelta(days=30)
            stmt = select(User).where(
                User.school_id == school_id,
                User.last_login_at >= recent_date
            )
            
            if pagination:
                from sqlalchemy import func
                total_stmt = select(func.count()).select_from(User).where(
                    User.school_id == school_id,
                    User.last_login_at >= recent_date
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
            logging.error(f"Error fetching active users for school {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def count_by_role(self, school_id: str, role: str) -> int:
        """Count users by role within a school"""
        try:
            from sqlalchemy import func
            stmt = select(func.count()).select_from(User).where(
                User.school_id == school_id,
                User.role == role
            )
            result = self.session.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            import logging
            logging.error(f"Error counting users by role {role}: {e}")
            return 0

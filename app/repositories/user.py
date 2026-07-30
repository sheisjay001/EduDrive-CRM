from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.entities import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str, school_id: str) -> Optional[User]:
        stmt = select(User).where(
            User.email == email,
            User.school_id == school_id
        )
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_school(self, school_id: str) -> List[User]:
        stmt = select(User).where(User.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def update_last_login(self, user: User) -> User:
        from datetime import datetime
        return self.update(user, last_login_at=datetime.utcnow())

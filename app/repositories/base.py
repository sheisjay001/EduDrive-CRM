from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, id: str) -> Optional[ModelType]:
        return self.session.get(self.model, id)

    def get_by_school_id(self, school_id: str) -> List[ModelType]:
        stmt = select(self.model).where(self.model.school_id == school_id)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

    def create(self, **kwargs) -> ModelType:
        db_obj = self.model(**kwargs)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, **kwargs) -> ModelType:
        for field, value in kwargs.items():
            setattr(db_obj, field, value)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ModelType) -> None:
        self.session.delete(db_obj)
        self.session.commit()

    def get_all(self) -> List[ModelType]:
        stmt = select(self.model)
        result = self.session.execute(stmt)
        return list(result.scalars().all())

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
from app.database.base import Base
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class PaginationParams:
    """Pagination parameters for queries"""
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = min(limit, 1000)  # Max limit of 1000


class FilterParams:
    """Filter parameters for queries"""
    def __init__(self, filters: Optional[Dict[str, Any]] = None):
        self.filters = filters or {}


class PaginatedResult:
    """Paginated result wrapper"""
    def __init__(self, items: List[Any], total: int, skip: int, limit: int):
        self.items = items
        self.total = total
        self.skip = skip
        self.limit = limit
        self.has_more = (skip + limit) < total


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, id: str, include_deleted: bool = False) -> Optional[ModelType]:
        """Get a single record by ID with optional soft delete support"""
        try:
            stmt = select(self.model).where(self.model.id == id)
            if hasattr(self.model, 'deleted_at') and not include_deleted:
                stmt = stmt.where(self.model.deleted_at.is_(None))
            result = self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by id {id}: {e}")
            return None

    def get_by_school_id(self, school_id: str, pagination: Optional[PaginationParams] = None) -> List[ModelType] | PaginatedResult:
        """Get records by school ID with optional pagination"""
        try:
            stmt = select(self.model).where(self.model.school_id == school_id)
            if hasattr(self.model, 'deleted_at'):
                stmt = stmt.where(self.model.deleted_at.is_(None))
            
            if pagination:
                total_stmt = select(func.count()).select_from(self.model).where(self.model.school_id == school_id)
                if hasattr(self.model, 'deleted_at'):
                    total_stmt = total_stmt.where(self.model.deleted_at.is_(None))
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
            logger.error(f"Error fetching {self.model.__name__} by school_id {school_id}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def create(self, **kwargs) -> ModelType:
        """Create a new record with error handling and logging"""
        try:
            db_obj = self.model(**kwargs)
            if hasattr(db_obj, 'created_at'):
                db_obj.created_at = datetime.utcnow()
            self.session.add(db_obj)
            self.session.commit()
            self.session.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with id {db_obj.id}")
            return db_obj
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise

    def update(self, db_obj: ModelType, **kwargs) -> ModelType:
        """Update a record with error handling and logging"""
        try:
            for field, value in kwargs.items():
                setattr(db_obj, field, value)
            if hasattr(db_obj, 'updated_at'):
                db_obj.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with id {db_obj.id}")
            return db_obj
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating {self.model.__name__} with id {db_obj.id}: {e}")
            raise

    def delete(self, db_obj: ModelType, soft_delete: bool = True) -> None:
        """Delete a record with soft delete support"""
        try:
            if soft_delete and hasattr(db_obj, 'deleted_at'):
                db_obj.deleted_at = datetime.utcnow()
                if hasattr(db_obj, 'updated_at'):
                    db_obj.updated_at = datetime.utcnow()
                self.session.commit()
                logger.info(f"Soft deleted {self.model.__name__} with id {db_obj.id}")
            else:
                self.session.delete(db_obj)
                self.session.commit()
                logger.info(f"Hard deleted {self.model.__name__} with id {db_obj.id}")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting {self.model.__name__} with id {db_obj.id}: {e}")
            raise

    def get_all(self, pagination: Optional[PaginationParams] = None, include_deleted: bool = False) -> List[ModelType] | PaginatedResult:
        """Get all records with optional pagination and soft delete filter"""
        try:
            stmt = select(self.model)
            if hasattr(self.model, 'deleted_at') and not include_deleted:
                stmt = stmt.where(self.model.deleted_at.is_(None))
            
            if pagination:
                total_stmt = select(func.count()).select_from(self.model)
                if hasattr(self.model, 'deleted_at') and not include_deleted:
                    total_stmt = total_stmt.where(self.model.deleted_at.is_(None))
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
            logger.error(f"Error fetching all {self.model.__name__}: {e}")
            return [] if not pagination else PaginatedResult([], 0, 0, 0)

    def bulk_create(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        """Bulk create records with transaction support"""
        try:
            db_objects = []
            for item in items:
                if hasattr(self.model, 'created_at'):
                    item['created_at'] = datetime.utcnow()
                db_obj = self.model(**item)
                db_objects.append(db_obj)
                self.session.add(db_obj)
            
            self.session.commit()
            for obj in db_objects:
                self.session.refresh(obj)
            
            logger.info(f"Bulk created {len(db_objects)} {self.model.__name__} records")
            return db_objects
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise

    def bulk_update(self, objects: List[ModelType], update_data: Dict[str, Any]) -> List[ModelType]:
        """Bulk update records with transaction support"""
        try:
            if hasattr(self.model, 'updated_at'):
                update_data['updated_at'] = datetime.utcnow()
            
            for obj in objects:
                for field, value in update_data.items():
                    setattr(obj, field, value)
            
            self.session.commit()
            for obj in objects:
                self.session.refresh(obj)
            
            logger.info(f"Bulk updated {len(objects)} {self.model.__name__} records")
            return objects
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error bulk updating {self.model.__name__}: {e}")
            raise

    def bulk_delete(self, objects: List[ModelType], soft_delete: bool = True) -> None:
        """Bulk delete records with soft delete support"""
        try:
            if soft_delete and hasattr(self.model, 'deleted_at'):
                for obj in objects:
                    obj.deleted_at = datetime.utcnow()
                    if hasattr(obj, 'updated_at'):
                        obj.updated_at = datetime.utcnow()
            else:
                for obj in objects:
                    self.session.delete(obj)
            
            self.session.commit()
            logger.info(f"Bulk deleted {len(objects)} {self.model.__name__} records")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error bulk deleting {self.model.__name__}: {e}")
            raise

    def count(self, filters: Optional[Dict[str, Any]] = None, include_deleted: bool = False) -> int:
        """Count records with optional filters"""
        try:
            stmt = select(func.count()).select_from(self.model)
            
            if hasattr(self.model, 'deleted_at') and not include_deleted:
                stmt = stmt.where(self.model.deleted_at.is_(None))
            
            if filters:
                conditions = []
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        conditions.append(getattr(self.model, field) == value)
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            result = self.session.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            return 0

    def exists(self, id: str) -> bool:
        """Check if a record exists by ID"""
        try:
            stmt = select(func.count()).select_from(self.model).where(self.model.id == id)
            if hasattr(self.model, 'deleted_at'):
                stmt = stmt.where(self.model.deleted_at.is_(None))
            result = self.session.execute(stmt)
            return (result.scalar() or 0) > 0
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {id}: {e}")
            return False

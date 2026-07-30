from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import SessionLocal
from app.models.entities import User, School
from app.repositories import UserRepository, SchoolRepository
from app.schemas.crm import AuthUser

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user_by_email(db: Session, email: str, school_id: Optional[str] = None) -> Optional[User]:
    user_repo = UserRepository(db)
    if school_id:
        return user_repo.get_by_email(email, school_id)
    return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[AuthUser]:
    user_repo = UserRepository(db)
    school_repo = SchoolRepository(db)
    
    # Try to find user by email across all schools
    from sqlalchemy import select
    stmt = select(User).where(User.email == email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    school = school_repo.get_by_id(user.school_id)
    if not school:
        return None
    
    return AuthUser(
        id=user.id,
        schoolId=user.school_id,
        role="school_admin",  # Default role for now
        fullName=user.full_name,
        email=user.email,
    )


def create_access_token(subject: str, extra: dict | None = None, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {
        "sub": subject,
        "exp": expire,
        "token_type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, extra: dict | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {
        "sub": subject,
        "exp": expire,
        "token_type": "refresh",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, str]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthUser:
    payload = decode_token(token)
    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not an access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # For demo mode, reconstruct user from token claims to avoid DB lookup.
    email = payload.get("sub")
    school_id = payload.get("schoolId")
    role = payload.get("role")
    full_name = payload.get("fullName")
    user_id = payload.get("user_id")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User information missing in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthUser(id=user_id or "", schoolId=school_id or "", role=role or "", fullName=full_name or "", email=email)


def decode_refresh_token(token: str) -> AuthUser:
    payload = decode_token(token)
    if payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not a refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Reconstruct user from refresh token claims
    email = payload.get("sub")
    school_id = payload.get("schoolId")
    role = payload.get("role")
    full_name = payload.get("fullName")
    user_id = payload.get("user_id")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User information missing in refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthUser(id=user_id or "", schoolId=school_id or "", role=role or "", fullName=full_name or "", email=email)


def create_tokens_for_user(user: AuthUser) -> tuple[str, str]:
    extra = {"schoolId": user.schoolId, "role": user.role, "fullName": user.fullName, "user_id": user.id}
    access_token = create_access_token(subject=user.email, extra=extra)
    refresh_token = create_refresh_token(subject=user.email, extra=extra)
    return access_token, refresh_token


def require_role(required: str):
    def _dependency(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if current_user.role != required:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return _dependency


def require_any_role(required_roles: list[str]):
    def _dependency(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if current_user.role not in required_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return _dependency


def has_permission(user: AuthUser, permission: str) -> bool:
    """Check if user has a specific permission based on their role"""
    role_permissions = {
        "super_admin": ["*"],
        "school_admin": ["dashboard:*", "admissions:*", "finance:*", "helpdesk:*", "staff:*", "reports:*", "settings:*"],
        "admissions_officer": ["dashboard:view", "admissions:*", "leads:*", "parents:view"],
        "bursar": ["dashboard:view", "finance:*", "invoices:*", "payments:*", "students:view"],
        "teacher": ["dashboard:view", "students:*", "attendance:*", "behavior:*", "academic:*", "parents:view"],
        "helpdesk_officer": ["dashboard:view", "helpdesk:*", "tickets:*", "parents:view"],
    }
    
    user_perms = role_permissions.get(user.role, [])
    
    # Check for wildcard permission
    if "*" in user_perms:
        return True
    
    # Check for exact permission match
    if permission in user_perms:
        return True
    
    # Check for wildcard prefix match (e.g., "admissions:*" matches "admissions:create")
    for perm in user_perms:
        if perm.endswith(":*") and permission.startswith(perm[:-2]):
            return True
    
    return False

from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.database.session import get_db
from app.schemas.crm import AuthUser

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str) -> Optional[AuthUser]:
    """Authenticate user using TiDB database"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        print(f"Attempting to authenticate user: {email}")
        
        # Query user from database
        query = """
            SELECT u.id, u.email, u.full_name, u.password_hash, u.status, u.is_active,
                   ur.role, ur.school_id, s.slug as school_slug
            FROM users u
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN schools s ON ur.school_id = s.id
            WHERE u.email = %s AND u.is_active = TRUE
        """
        cursor.execute(query, (email,))
        user_data = cursor.fetchone()
        
        if not user_data:
            print("User not found or inactive")
            return None
        
        # Verify password
        if not verify_password(password, user_data['password_hash']):
            print("Invalid password")
            return None
        
        # Update last login
        update_query = "UPDATE users SET last_login_at = NOW() WHERE id = %s"
        cursor.execute(update_query, (user_data['id'],))
        db.commit()
        
        role = user_data.get('role', 'school_admin') or 'school_admin'
        school_id = user_data.get('school_id', '') or ''
        school_slug = user_data.get('school_slug', '') or ''
        
        print(f"Authenticated user: {user_data['email']} with role: {role}, school_slug: {school_slug}")
        
        return AuthUser(
            id=user_data['id'],
            schoolId=school_id,
            schoolSlug=school_slug,
            role=role,
            fullName=user_data['full_name'],
            email=user_data['email'],
        )
    except Exception as e:
        print(f"Authentication error: {e}")
        import traceback
        traceback.print_exc()
        return None


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

    # Reconstruct user from token claims
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
    extra = {"schoolId": user.schoolId, "schoolSlug": user.schoolSlug, "role": user.role, "fullName": user.fullName, "user_id": user.id}
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
        "super_admin": ["*"],  # Full system access
        "school_admin": ["dashboard:view", "admissions:*", "leads:*", "families:*", "parents:*", "students:*", "finance:*", "invoices:*", "payments:*", "messaging:*", "helpdesk:*", "tickets:*", "staff:*", "reports:*", "settings:*", "calendar:*", "terms:*", "classes:*", "analytics:*", "debtors:*", "bulk-billing:*", "receipts:*", "lost-leads:*", "workload:*", "user-admin:*", "activity:*", "frontdesk:*", "lifecycle:*", "transport:*"],
        "admissions_officer": ["dashboard:view", "admissions:view", "leads:*", "parents:view", "calendar:*", "lost-leads:*", "messaging:view", "messaging:create", "reminders:*"],
        "bursar": ["dashboard:view", "finance:view", "invoices:*", "payments:*", "students:view", "debtors:*", "bulk-billing:*", "receipts:*", "reports:view", "messaging:view", "reminders:*"],
        "teacher": ["dashboard:view", "students:view", "attendance:*", "behavior:*", "academic:*", "parents:view", "lifecycle:*", "classes:view", "workload:view-own", "reports:view-own"],
        "helpdesk_officer": ["dashboard:view", "helpdesk:*", "tickets:*", "parents:view", "students:view"],
        "parent": ["dashboard:view", "students:view-own", "tickets:create", "tickets:view-own", "payments:create", "payments:view-own", "invoices:view-own", "receipts:view-own", "lifecycle:view-own", "transport:view-own", "messages:view-own"],
        "student": ["dashboard:view", "students:view-self", "tickets:create", "tickets:view-own", "lifecycle:view-self", "attendance:view-self", "academic:view-self"],
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
    
    # Normalize data-scoped suffixes: tickets:view-own -> tickets:view
    def normalize_action(p: str) -> str:
        for suffix in ("-own", "-self"):
            idx = p.rfind(suffix)
            if idx != -1 and idx > p.find(":"):
                return p[:idx]
        return p
    
    normalized_permission = normalize_action(permission)
    if normalized_permission != permission and normalized_permission in user_perms:
        return True
    for perm in user_perms:
        normalized_grant = normalize_action(perm)
        if normalized_grant == normalized_permission:
            return True
        if normalized_grant.endswith(":*") and normalized_permission.startswith(normalized_grant[:-2]):
            return True
    
    return False

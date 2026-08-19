from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/user-admin", tags=["user-admin"])

class PermissionGrantRequest(BaseModel):
    user_id: str
    permission_name: str
    permission_category: str
    can_create: bool = False
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False
    expires_at: Optional[str]

class PermissionRevokeRequest(BaseModel):
    user_id: str
    permission_name: str

@router.post("/permissions/grant")
async def grant_permission(
    request: PermissionGrantRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Grant permission to a user"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        permission_id = supabase.rpc('grant_user_permission', {
            'p_user_id': request.user_id,
            'p_permission_name': request.permission_name,
            'p_permission_category': request.permission_category,
            'p_can_create': request.can_create,
            'p_can_read': request.can_read,
            'p_can_update': request.can_update,
            'p_can_delete': request.can_delete,
            'p_granted_by': current_user.id,
            'p_expires_at': request.expires_at,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "permission_id": permission_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/permissions/revoke")
async def revoke_permission(
    request: PermissionRevokeRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Revoke permission from a user"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        supabase.rpc('revoke_user_permission', {
            'p_user_id': request.user_id,
            'p_permission_name': request.permission_name
        }).execute()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/permissions/check/{user_id}/{permission_name}/{action}")
async def check_permission(
    user_id: str,
    permission_name: str,
    action: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Check if user has specific permission"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        has_permission = supabase.rpc('check_user_permission', {
            'p_user_id': user_id,
            'p_permission_name': permission_name,
            'p_required_action': action
        }).execute()
        
        return {"has_permission": has_permission.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/roles/apply")
async def apply_role_permissions(
    user_id: str,
    role: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Apply role-based permissions to a user"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        applied_count = supabase.rpc('apply_role_permissions', {
            'p_user_id': user_id,
            'p_role': role,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "applied_count": applied_count.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/permissions/summary")
async def get_permissions_summary(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get user permissions summary"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('user_permissions_summary').select('*').execute()
        return {"summary": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity-summary")
async def get_user_activity_summary(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get user activity summary"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('user_activity_summary').select('*').execute()
        return {"activity": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/role-matrix")
async def get_role_permission_matrix(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get role permission matrix"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('role_permission_matrix').select('*').execute()
        return {"matrix": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

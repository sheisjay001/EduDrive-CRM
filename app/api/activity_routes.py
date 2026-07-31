from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/activity", tags=["activity"])

class ActivityLog(BaseModel):
    id: str
    user_id: str
    user_name: str
    user_role: str
    action_type: str
    entity_type: str
    entity_id: Optional[str]
    old_values: Optional[dict]
    new_values: Optional[dict]
    description: Optional[str]
    created_at: datetime

class ActivityLogRequest(BaseModel):
    action_type: str
    entity_type: str
    entity_id: Optional[str]
    old_values: Optional[dict]
    new_values: Optional[dict]
    description: Optional[str]

@router.post("/log")
async def log_activity(
    request: ActivityLogRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Log a user activity"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('log_activity', {
            'p_user_id': current_user.id,
            'p_user_name': current_user.fullName,
            'p_user_role': current_user.role,
            'p_action_type': request.action_type,
            'p_entity_type': request.entity_type,
            'p_entity_id': request.entity_id,
            'p_old_values': request.old_values,
            'p_new_values': request.new_values,
            'p_description': request.description,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "log_id": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
async def get_recent_activity(
    limit: int = Query(50, ge=1, le=100),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get recent activity logs"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('activity_logs').select('*')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return {"activities": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_activity(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get activity logs for a specific user"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        result = supabase.table('activity_logs').select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', cutoff_date.isoformat())\
            .order('created_at', desc=True)\
            .execute()
        
        return {"activities": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_activity(
    entity_type: str,
    entity_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get activity logs for a specific entity"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('activity_logs').select('*')\
            .eq('entity_type', entity_type)\
            .eq('entity_id', entity_id)\
            .order('created_at', desc=True)\
            .execute()
        
        return {"activities": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_activity_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get activity statistics"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get total actions by user
        user_actions = supabase.table('activity_logs').select('user_id, user_name, user_role, count(*)')\
            .gte('created_at', cutoff_date.isoformat())\
            .execute()
        
        # Get actions by type
        type_actions = supabase.table('activity_logs').select('action_type, count(*)')\
            .gte('created_at', cutoff_date.isoformat())\
            .execute()
        
        return {
            "user_actions": user_actions.data,
            "type_actions": type_actions.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

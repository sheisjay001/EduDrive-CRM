from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import date, time
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/frontdesk", tags=["frontdesk"])

class DailyLogCreateRequest(BaseModel):
    log_date: date
    calls_logged: int = 0
    calls_answered: int = 0
    calls_missed: int = 0
    calls_followed_up: int = 0
    visitors_checked_in: int = 0
    visitors_checked_out: int = 0
    walk_in_inquiries: int = 0
    new_leads_created: int = 0
    lead_follow_ups_completed: int = 0
    tours_scheduled: int = 0
    messages_sent: int = 0
    complaints_logged: int = 0
    tasks_completed: int = 0
    notes: Optional[str]
    performance_rating: Optional[str]
    shift_start: Optional[time]
    shift_end: Optional[time]

class ActivityLogRequest(BaseModel):
    daily_log_id: str
    activity_type: str
    activity_description: str
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    notes: Optional[str]

@router.post("/daily-log")
async def create_or_update_daily_log(
    request: DailyLogCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create or update daily front-desk log"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('upsert_frontdesk_log', {
            'p_log_date': request.log_date.isoformat(),
            'p_staff_id': current_user.id,
            'p_staff_name': current_user.fullName,
            'p_staff_role': current_user.role,
            'p_calls_logged': request.calls_logged,
            'p_calls_answered': request.calls_answered,
            'p_calls_missed': request.calls_missed,
            'p_calls_followed_up': request.calls_followed_up,
            'p_visitors_checked_in': request.visitors_checked_in,
            'p_visitors_checked_out': request.visitors_checked_out,
            'p_walk_in_inquiries': request.walk_in_inquiries,
            'p_new_leads_created': request.new_leads_created,
            'p_lead_follow_ups_completed': request.lead_follow_ups_completed,
            'p_tours_scheduled': request.tours_scheduled,
            'p_messages_sent': request.messages_sent,
            'p_complaints_logged': request.complaints_logged,
            'p_tasks_completed': request.tasks_completed,
            'p_notes': request.notes,
            'p_performance_rating': request.performance_rating,
            'p_shift_start': request.shift_start.isoformat() if request.shift_start else None,
            'p_shift_end': request.shift_end.isoformat() if request.shift_end else None,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "log_id": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activity")
async def log_activity(
    request: ActivityLogRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Log a specific front-desk activity"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('log_frontdesk_activity', {
            'p_daily_log_id': request.daily_log_id,
            'p_activity_type': request.activity_type,
            'p_activity_description': request.activity_description,
            'p_related_entity_type': request.related_entity_type,
            'p_related_entity_id': request.related_entity_id,
            'p_notes': request.notes,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "activity_id": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily-summary")
async def get_daily_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get daily front-desk summary"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('frontdesk_daily_summary').select('*')
        
        if start_date:
            query = query.gte('log_date', start_date.isoformat())
        if end_date:
            query = query.lte('log_date', end_date.isoformat())
        
        result = query.order('log_date', desc=True).execute()
        
        return {"summary": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/staff-performance")
async def get_staff_performance(
    days: int = Query(30, ge=1, le=365),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get staff performance metrics"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('frontdesk_staff_performance').select('*').execute()
        return {"performance": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/{daily_log_id}")
async def get_daily_activities(
    daily_log_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get activities for a specific daily log"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('frontdesk_activities').select('*')\
            .eq('daily_log_id', daily_log_id)\
            .order('activity_time', desc=True)\
            .execute()
        
        return {"activities": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-logs")
async def get_my_logs(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get current user's daily logs"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('frontdesk_daily_logs').select('*')\
            .eq('staff_id', current_user.id)
        
        if start_date:
            query = query.gte('log_date', start_date.isoformat())
        if end_date:
            query = query.lte('log_date', end_date.isoformat())
        
        result = query.order('log_date', desc=True).execute()
        
        return {"logs": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

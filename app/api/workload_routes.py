from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/workload", tags=["workload"])

class WorkloadUpdateRequest(BaseModel):
    staff_id: str
    staff_name: str
    staff_role: str
    task_type: str
    task_change: int  # +1 to add, -1 to remove

@router.post("/update")
async def update_staff_workload(
    request: WorkloadUpdateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Update staff workload for a task type"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        supabase.rpc('update_staff_workload', {
            'p_staff_id': request.staff_id,
            'p_staff_name': request.staff_name,
            'p_staff_role': request.staff_role,
            'p_task_type': request.task_type,
            'p_task_change': request.task_change,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current")
async def get_current_workload(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get current workload status for all staff"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('current_workload_status').select('*').execute()
        return {"workload": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary-by-role")
async def get_workload_summary_by_role(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get workload summary grouped by role"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('workload_summary_by_role').select('*').execute()
        return {"summary": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-trends")
async def get_performance_trends(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get staff performance trends over time"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('staff_performance_trends').select('*').execute()
        return {"trends": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

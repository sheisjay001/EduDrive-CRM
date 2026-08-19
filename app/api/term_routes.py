from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/terms", tags=["terms"])

class SessionCreateRequest(BaseModel):
    session_name: str
    session_code: str
    start_date: date
    end_date: date
    description: Optional[str]

class TermCreateRequest(BaseModel):
    session_id: str
    term_name: str
    term_code: str
    term_order: int
    start_date: date
    end_date: date
    fee_structure_id: Optional[str]
    description: Optional[str]

class TermDateRequest(BaseModel):
    term_id: str
    date_type: str
    date_name: str
    date_value: date
    is_school_day: bool = True
    notes: Optional[str]

@router.post("/sessions")
async def create_academic_session(
    request: SessionCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create an academic session"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        session_id = supabase.rpc('create_academic_session', {
            'p_session_name': request.session_name,
            'p_session_code': request.session_code,
            'p_start_date': request.start_date,
            'p_end_date': request.end_date,
            'p_description': request.description,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "session_id": session_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_academic_sessions(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all academic sessions"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('academic_sessions').select('*').order('start_date', desc=True).execute()
        return {"sessions": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/terms")
async def create_academic_term(
    request: TermCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create an academic term"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        term_id = supabase.rpc('create_academic_term', {
            'p_session_id': request.session_id,
            'p_term_name': request.term_name,
            'p_term_code': request.term_code,
            'p_term_order': request.term_order,
            'p_start_date': request.start_date,
            'p_end_date': request.end_date,
            'p_fee_structure_id': request.fee_structure_id,
            'p_description': request.description,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "term_id": term_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/terms")
async def get_academic_terms(
    session_id: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get academic terms"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('academic_terms').select('*')
        
        if session_id:
            query = query.eq('session_id', session_id)
        
        result = query.order('term_order').execute()
        return {"terms": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current")
async def get_current_term(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get current academic term"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('get_current_term', {'p_school_id': current_user.schoolId}).execute()
        return {"current_term": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/terms/{term_id}/set-current")
async def set_current_term(
    term_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Set a term as current"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        supabase.rpc('set_current_term', {'p_term_id': term_id}).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/term-dates")
async def add_term_date(
    request: TermDateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Add an important date to a term"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        date_id = supabase.rpc('add_term_date', {
            'p_term_id': request.term_id,
            'p_date_type': request.date_type,
            'p_date_name': request.date_name,
            'p_date_value': request.date_value,
            'p_is_school_day': request.is_school_day,
            'p_notes': request.notes,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "date_id": date_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar")
async def get_academic_calendar(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get full academic calendar"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('academic_calendar').select('*').execute()
        return {"calendar": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])

class LifecycleLogCreateRequest(BaseModel):
    student_id: str
    log_type: str  # 'academic', 'disciplinary', 'medical', 'attendance', 'achievement', 'fee_payment'
    term: str
    academic_year: str
    subject: Optional[str]
    grade: Optional[str]
    score: Optional[float]
    teacher_comments: Optional[str]
    incident_type: Optional[str]
    incident_date: Optional[date]
    severity: Optional[str]
    action_taken: Optional[str]
    resolved: Optional[bool]
    resolution_date: Optional[date]
    medical_condition: Optional[str]
    treatment: Optional[str]
    doctor_name: Optional[str]
    follow_up_required: Optional[bool]
    follow_up_date: Optional[date]
    attendance_date: Optional[date]
    attendance_status: Optional[str]
    absence_reason: Optional[str]
    achievement_type: Optional[str]
    achievement_date: Optional[date]
    description: Optional[str]
    award_level: Optional[str]
    fee_type: Optional[str]
    amount_paid: Optional[float]
    payment_date: Optional[date]
    payment_method: Optional[str]
    term_balance: Optional[float]
    notes: Optional[str]

@router.post("/logs")
async def create_lifecycle_log(
    request: LifecycleLogCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new student lifecycle log entry"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('add_lifecycle_log', {
            'p_student_id': request.student_id,
            'p_log_type': request.log_type,
            'p_term': request.term,
            'p_academic_year': request.academic_year,
            'p_subject': request.subject,
            'p_grade': request.grade,
            'p_score': request.score,
            'p_teacher_comments': request.teacher_comments,
            'p_incident_type': request.incident_type,
            'p_incident_date': request.incident_date.isoformat() if request.incident_date else None,
            'p_severity': request.severity,
            'p_action_taken': request.action_taken,
            'p_resolved': request.resolved,
            'p_resolution_date': request.resolution_date.isoformat() if request.resolution_date else None,
            'p_medical_condition': request.medical_condition,
            'p_treatment': request.treatment,
            'p_doctor_name': request.doctor_name,
            'p_follow_up_required': request.follow_up_required,
            'p_follow_up_date': request.follow_up_date.isoformat() if request.follow_up_date else None,
            'p_attendance_date': request.attendance_date.isoformat() if request.attendance_date else None,
            'p_attendance_status': request.attendance_status,
            'p_absence_reason': request.absence_reason,
            'p_achievement_type': request.achievement_type,
            'p_achievement_date': request.achievement_date.isoformat() if request.achievement_date else None,
            'p_description': request.description,
            'p_award_level': request.award_level,
            'p_fee_type': request.fee_type,
            'p_amount_paid': request.amount_paid,
            'p_payment_date': request.payment_date.isoformat() if request.payment_date else None,
            'p_payment_method': request.payment_method,
            'p_term_balance': request.term_balance,
            'p_notes': request.notes,
            'p_recorded_by': current_user.id,
            'p_recorded_by_name': current_user.fullName,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "log_id": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/student/{student_id}")
async def get_student_lifecycle(
    student_id: str,
    log_type: Optional[str] = None,
    term: Optional[str] = None,
    academic_year: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get lifecycle logs for a specific student"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('student_lifecycle_logs').select('*').eq('student_id', student_id)
        
        if log_type:
            query = query.eq('log_type', log_type)
        if term:
            query = query.eq('term', term)
        if academic_year:
            query = query.eq('academic_year', academic_year)
        
        result = query.order('created_at', desc=True).execute()
        
        return {"logs": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/disciplinary")
async def get_disciplinary_records(
    student_id: Optional[str] = None,
    term: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get disciplinary records"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('disciplinary_records').select('*')
        
        if student_id:
            query = query.eq('student_id', student_id)
        if term:
            query = query.eq('term', term)
        
        result = query.order('incident_date', desc=True).execute()
        
        return {"records": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/academic")
async def get_academic_performance(
    student_id: Optional[str] = None,
    term: Optional[str] = None,
    academic_year: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get academic performance records"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('academic_performance').select('*')
        
        if student_id:
            query = query.eq('student_id', student_id)
        if term:
            query = query.eq('term', term)
        if academic_year:
            query = query.eq('academic_year', academic_year)
        
        result = query.order('term', desc=True).execute()
        
        return {"performance": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/student/{student_id}")
async def get_student_summary(
    student_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get term-by-term summary for a student"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('student_term_summary').select('*')\
            .eq('student_id', student_id)\
            .order('academic_year', desc=True)\
            .order('term', desc=True)\
            .execute()
        
        return {"summary": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/logs/{log_id}/resolve")
async def resolve_disciplinary_record(
    log_id: str,
    resolution_date: date,
    action_taken: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Resolve a disciplinary record"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('student_lifecycle_logs').update({
            'resolved': True,
            'resolution_date': resolution_date.isoformat(),
            'action_taken': action_taken
        }).eq('id', log_id).execute()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

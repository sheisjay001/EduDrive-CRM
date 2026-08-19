from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/classes", tags=["classes"])

class ClassCreateRequest(BaseModel):
    class_name: str
    class_code: str
    class_level: str
    section: Optional[str]
    capacity: int = 40
    class_teacher_id: Optional[str]
    class_teacher_name: Optional[str]
    academic_session_id: Optional[str]
    description: Optional[str]

class SubjectRequest(BaseModel):
    class_id: str
    subject_name: str
    subject_code: Optional[str]
    teacher_id: Optional[str]
    teacher_name: Optional[str]
    periods_per_week: int = 5
    is_core_subject: bool = False

class EnrollmentRequest(BaseModel):
    student_id: str
    class_id: str
    term_id: Optional[str]
    previous_class_id: Optional[str]

@router.post("/")
async def create_class(
    request: ClassCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new class"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        class_id = supabase.rpc('create_class', {
            'p_class_name': request.class_name,
            'p_class_code': request.class_code,
            'p_class_level': request.class_level,
            'p_section': request.section,
            'p_capacity': request.capacity,
            'p_class_teacher_id': request.class_teacher_id,
            'p_class_teacher_name': request.class_teacher_name,
            'p_academic_session_id': request.academic_session_id,
            'p_description': request.description,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "class_id": class_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_classes(
    class_level: Optional[str] = None,
    is_active: bool = True,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all classes"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('classes').select('*').eq('is_active', is_active)
        
        if class_level:
            query = query.eq('class_level', class_level)
        
        result = query.order('class_level', 'class_code').execute()
        return {"classes": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/structure")
async def get_class_structure(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get detailed class structure with enrollment and subjects"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('class_structure').select('*').execute()
        return {"structure": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subjects")
async def add_class_subject(
    request: SubjectRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Add a subject to a class"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        subject_id = supabase.rpc('add_class_subject', {
            'p_class_id': request.class_id,
            'p_subject_name': request.subject_name,
            'p_subject_code': request.subject_code,
            'p_teacher_id': request.teacher_id,
            'p_teacher_name': request.teacher_name,
            'p_periods_per_week': request.periods_per_week,
            'p_is_core_subject': request.is_core_subject,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "subject_id": subject_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{class_id}/subjects")
async def get_class_subjects(
    class_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get subjects for a class"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('class_subjects').select('*').eq('class_id', class_id).eq('is_active', True).execute()
        return {"subjects": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enrollments")
async def enroll_student(
    request: EnrollmentRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Enroll a student in a class"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        enrollment_id = supabase.rpc('enroll_student_in_class', {
            'p_student_id': request.student_id,
            'p_class_id': request.class_id,
            'p_term_id': request.term_id,
            'p_previous_class_id': request.previous_class_id,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "enrollment_id": enrollment_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/promote")
async def promote_students(
    class_id: str,
    next_class_id: str,
    term_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Promote students from one class to the next"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        promoted_count = supabase.rpc('promote_students', {
            'p_class_id': class_id,
            'p_next_class_id': next_class_id,
            'p_term_id': term_id,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "promoted_count": promoted_count.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher-load")
async def get_teacher_subject_load(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get teacher subject load across all classes"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('teacher_subject_load').select('*').execute()
        return {"teacher_load": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

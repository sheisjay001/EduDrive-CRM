from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional, List
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser
from app.database.session import get_supabase_client
import csv
import io

router = APIRouter(prefix="/students", tags=["students"])

class StudentCreateRequest(BaseModel):
    first_name: str
    last_name: str
    admission_no: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[str]
    family_id: Optional[str]
    class_id: Optional[str]
    lead_id: Optional[str]

class StudentUpdateRequest(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    admission_no: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[str]
    family_id: Optional[str]
    class_id: Optional[str]
    status: Optional[str]

def check_student_permission(user: AuthUser) -> bool:
    """Check if user has permission to manage students"""
    allowed_roles = ["school_admin", "admission_officer", "teacher"]
    return user.role in allowed_roles

@router.post("/")
async def create_student(
    request: StudentCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new student (school_admin, admission_officer, teacher)"""
    if not check_student_permission(current_user):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('students').insert({
            'school_id': current_user.schoolId,
            'first_name': request.first_name,
            'last_name': request.last_name,
            'admission_no': request.admission_no,
            'gender': request.gender,
            'date_of_birth': request.date_of_birth,
            'family_id': request.family_id,
            'class_id': request.class_id,
            'lead_id': request.lead_id,
            'status': 'active'
        }).execute()
        
        return {"success": True, "student": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_students(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all students for the school"""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('students').select('*').eq('school_id', current_user.schoolId).execute()
        return {"students": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{student_id}")
async def get_student(
    student_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get a specific student by ID"""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('students').select('*').eq('id', student_id).eq('school_id', current_user.schoolId).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {"student": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{student_id}")
async def update_student(
    student_id: str,
    request: StudentUpdateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Update student information (school_admin, admission_officer, teacher)"""
    if not check_student_permission(current_user):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    supabase = get_supabase_client()
    
    try:
        update_data = {}
        if request.first_name:
            update_data['first_name'] = request.first_name
        if request.last_name:
            update_data['last_name'] = request.last_name
        if request.admission_no:
            update_data['admission_no'] = request.admission_no
        if request.gender:
            update_data['gender'] = request.gender
        if request.date_of_birth:
            update_data['date_of_birth'] = request.date_of_birth
        if request.family_id:
            update_data['family_id'] = request.family_id
        if request.class_id:
            update_data['class_id'] = request.class_id
        if request.status:
            update_data['status'] = request.status
        
        result = supabase.table('students').update(update_data).eq('id', student_id).eq('school_id', current_user.schoolId).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {"success": True, "student": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Delete a student (school_admin only)"""
    if current_user.role != "school_admin":
        raise HTTPException(status_code=403, detail="Only school admins can delete students")
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('students').delete().eq('id', student_id).eq('school_id', current_user.schoolId).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import/csv")
async def import_students_csv(
    file: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_user)
):
    """Import students from CSV file (school_admin, admission_officer, teacher)"""
    if not check_student_permission(current_user):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    supabase = get_supabase_client()
    
    try:
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8'))
        csv_reader = csv.DictReader(csv_file)
        
        students_created = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                student_data = {
                    'school_id': current_user.schoolId,
                    'first_name': row.get('first_name', '').strip(),
                    'last_name': row.get('last_name', '').strip(),
                    'admission_no': row.get('admission_no', '').strip() or None,
                    'gender': row.get('gender', '').strip() or None,
                    'date_of_birth': row.get('date_of_birth', '').strip() or None,
                    'status': 'active'
                }
                
                if not student_data['first_name'] or not student_data['last_name']:
                    errors.append(f"Row {row_num}: Missing first_name or last_name")
                    continue
                
                result = supabase.table('students').insert(student_data).execute()
                students_created.append(result.data[0])
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "success": True,
            "students_created": len(students_created),
            "students": students_created,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

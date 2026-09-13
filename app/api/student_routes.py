from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Optional, List
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser
from app.database.session import get_db
import csv
import io
import uuid

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
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Check school's student limit
        cursor.execute("SELECT student_count FROM schools WHERE id = %s", (current_user.schoolId,))
        school = cursor.fetchone()
        
        if school and school.get('student_count') is not None:
            # Count current students
            cursor.execute("SELECT COUNT(*) as count FROM students WHERE school_id = %s", (current_user.schoolId,))
            current_count = cursor.fetchone()['count']
            
            if current_count >= school['student_count']:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Student limit exceeded. You have {current_count} students but your plan allows only {school['student_count']}. Please upgrade your subscription to add more students."
                )
        
        student_id = str(uuid.uuid4())
        query = """
            INSERT INTO students (id, school_id, first_name, last_name, admission_no, gender, date_of_birth, family_id, class_id, lead_id, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (
            student_id,
            current_user.schoolId,
            request.first_name,
            request.last_name,
            request.admission_no,
            request.gender,
            request.date_of_birth,
            request.family_id,
            request.class_id,
            request.lead_id,
            'active'
        ))
        db.commit()
        
        return {"success": True, "student_id": student_id}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/")
async def get_students(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all students for the school"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        query = "SELECT * FROM students WHERE school_id = %s"
        cursor.execute(query, (current_user.schoolId,))
        students = cursor.fetchall()
        return {"students": students}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.get("/{student_id}")
async def get_student(
    student_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get a specific student by ID"""
    db = get_db()
    cursor = db.cursor()
    
    try:
        query = "SELECT * FROM students WHERE id = %s AND school_id = %s"
        cursor.execute(query, (student_id, current_user.schoolId))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"student": student}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.patch("/{student_id}")
async def update_student(
    student_id: str,
    request: StudentUpdateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Update student information (school_admin, admission_officer, teacher)"""
    if not check_student_permission(current_user):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    db = get_db()
    cursor = db.cursor()
    
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
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        set_clause = ", ".join([f"{k} = %s" for k in update_data.keys()])
        values = list(update_data.values()) + [student_id, current_user.schoolId]
        
        query = f"UPDATE students SET {set_clause}, updated_at = NOW() WHERE id = %s AND school_id = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        
        db.commit()
        return {"success": True}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

@router.delete("/{student_id}")
async def delete_student(
    student_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Delete a student (school_admin only)"""
    if current_user.role != "school_admin":
        raise HTTPException(status_code=403, detail="Only school admins can delete students")
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        query = "DELETE FROM students WHERE id = %s AND school_id = %s"
        cursor.execute(query, (student_id, current_user.schoolId))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        
        db.commit()
        return {"success": True}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

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
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8'))
        csv_reader = csv.DictReader(csv_file)
        
        imported_count = 0
        for row in csv_reader:
            student_id = str(uuid.uuid4())
            query = """
                INSERT INTO students (id, school_id, first_name, last_name, admission_no, gender, date_of_birth, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (
                student_id,
                current_user.schoolId,
                row.get('first_name', ''),
                row.get('last_name', ''),
                row.get('admission_no', ''),
                row.get('gender', ''),
                row.get('date_of_birth', None),
                'active'
            ))
            imported_count += 1
        
        db.commit()
        return {"success": True, "imported": imported_count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()

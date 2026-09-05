from datetime import datetime, date
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import get_current_user, require_role
from app.database.session import get_supabase_client

router = APIRouter()


# Pydantic Models
class StudentResponse(BaseModel):
    id: int
    full_name: str
    admission_no: str
    student_class: str
    gender: Optional[str]
    date_of_birth: Optional[str]
    parent_phone: Optional[str]


class AttendanceCreate(BaseModel):
    student_id: int
    date: str
    status: str = "present"
    remark: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    admission_no: str
    student_class: str
    date: str
    status: str
    remark: Optional[str]


class BulkAttendanceCreate(BaseModel):
    date: str
    attendance_records: List[Dict[str, Any]]  # [{"student_id": 1, "status": "present"}]


# Teacher: Get My Students (based on assigned classes)
@router.get("/teacher/my-students", response_model=List[StudentResponse])
async def get_my_students(
    current_user = Depends(require_role(["teacher"]))
):
    supabase = get_supabase_client()
    
    # Get teacher's assigned classes
    teacher_result = supabase.table("users").select("assigned_classes").eq("id", current_user["id"]).execute()
    if not teacher_result.data:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    assigned_classes = teacher_result.data[0].get("assigned_classes", "")
    class_list = [c.strip() for c in assigned_classes.split(',') if c.strip()]
    
    try:
        if not class_list or "all" in assigned_classes:
            # Get all students
            result = supabase.table("students").select("*").order("class, full_name").execute()
        else:
            # Get students in assigned classes
            result = supabase.table("students").select("*").in_("class", class_list).order("class, full_name").execute()
        
        return [
            StudentResponse(
                id=s["id"],
                full_name=s["full_name"],
                admission_no=s["admission_no"],
                student_class=s["class"],
                gender=s.get("gender"),
                date_of_birth=s.get("date_of_birth"),
                parent_phone=s.get("parent_phone")
            )
            for s in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch students: {str(e)}")


# Teacher: Get Attendance History for My Students
@router.get("/teacher/attendance", response_model=List[AttendanceResponse])
async def get_teacher_attendance(
    filter_date: Optional[str] = None,
    filter_class: Optional[str] = None,
    current_user = Depends(require_role(["teacher"]))
):
    supabase = get_supabase_client()
    
    # Get teacher's assigned classes
    teacher_result = supabase.table("users").select("assigned_classes").eq("id", current_user["id"]).execute()
    if not teacher_result.data:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    assigned_classes = teacher_result.data[0].get("assigned_classes", "")
    class_list = [c.strip() for c in assigned_classes.split(',') if c.strip()]
    
    try:
        # Build query
        query = supabase.table("teacher_attendance").select("*, students(full_name, admission_no, class)").eq("teacher_id", current_user["id"])
        
        if filter_date:
            query = query.eq("date", filter_date)
        
        if filter_class:
            query = query.filter("students.class", "eq", filter_class)
        
        result = query.order("date", desc=True).limit(100).execute()
        
        return [
            AttendanceResponse(
                id=a["id"],
                student_id=a["student_id"],
                student_name=a["students"]["full_name"],
                admission_no=a["students"]["admission_no"],
                student_class=a["students"]["class"],
                date=a["date"],
                status=a["status"],
                remark=a.get("remark")
            )
            for a in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch attendance: {str(e)}")


# Teacher: Create Attendance Record
@router.post("/teacher/attendance", response_model=AttendanceResponse)
async def create_attendance(
    attendance_data: AttendanceCreate,
    current_user = Depends(require_role(["teacher"]))
):
    supabase = get_supabase_client()
    
    # Validate student is in teacher's assigned classes
    teacher_result = supabase.table("users").select("assigned_classes").eq("id", current_user["id"]).execute()
    assigned_classes = teacher_result.data[0].get("assigned_classes", "")
    
    student_result = supabase.table("students").select("*").eq("id", attendance_data.student_id).execute()
    if not student_result.data:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_class = student_result.data[0]["class"]
    
    # Check if teacher is assigned to this class
    if "all" not in assigned_classes and student_class not in [c.strip() for c in assigned_classes.split(',')]:
        raise HTTPException(status_code=403, detail="You are not authorized to mark attendance for this student")
    
    try:
        # Check if attendance already exists
        existing = supabase.table("teacher_attendance").select("*").eq("student_id", attendance_data.student_id).eq("teacher_id", current_user["id"]).eq("date", attendance_data.date).execute()
        
        if existing.data:
            # Update existing
            result = supabase.table("teacher_attendance").update({
                "status": attendance_data.status,
                "remark": attendance_data.remark
            }).eq("id", existing.data[0]["id"]).execute()
            
            return AttendanceResponse(
                id=result.data[0]["id"],
                student_id=result.data[0]["student_id"],
                student_name=student_result.data[0]["full_name"],
                admission_no=student_result.data[0]["admission_no"],
                student_class=student_result.data[0]["class"],
                date=result.data[0]["date"],
                status=result.data[0]["status"],
                remark=result.data[0].get("remark")
            )
        else:
            # Create new
            result = supabase.table("teacher_attendance").insert({
                "student_id": attendance_data.student_id,
                "teacher_id": current_user["id"],
                "date": attendance_data.date,
                "status": attendance_data.status,
                "remark": attendance_data.remark
            }).execute()
            
            return AttendanceResponse(
                id=result.data[0]["id"],
                student_id=result.data[0]["student_id"],
                student_name=student_result.data[0]["full_name"],
                admission_no=student_result.data[0]["admission_no"],
                student_class=student_result.data[0]["class"],
                date=result.data[0]["date"],
                status=result.data[0]["status"],
                remark=result.data[0].get("remark")
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create attendance: {str(e)}")


# Teacher: Bulk Attendance Marking
@router.post("/teacher/attendance/bulk")
async def bulk_attendance(
    bulk_data: BulkAttendanceCreate,
    current_user = Depends(require_role(["teacher"]))
):
    supabase = get_supabase_client()
    
    # Get teacher's assigned classes
    teacher_result = supabase.table("users").select("assigned_classes").eq("id", current_user["id"]).execute()
    assigned_classes = teacher_result.data[0].get("assigned_classes", "")
    
    success_count = 0
    fail_count = 0
    
    try:
        for record in bulk_data.attendance_records:
            student_id = record.get("student_id")
            status = record.get("status", "present")
            remark = record.get("remark")
            
            if not student_id:
                fail_count += 1
                continue
            
            # Validate student is in teacher's assigned classes
            student_result = supabase.table("students").select("*").eq("id", student_id).execute()
            if not student_result.data:
                fail_count += 1
                continue
            
            student_class = student_result.data[0]["class"]
            
            # Check if teacher is assigned to this class
            if "all" not in assigned_classes and student_class not in [c.strip() for c in assigned_classes.split(',')]:
                fail_count += 1
                continue
            
            # Check if attendance already exists
            existing = supabase.table("teacher_attendance").select("*").eq("student_id", student_id).eq("teacher_id", current_user["id"]).eq("date", bulk_data.date).execute()
            
            if existing.data:
                # Update existing
                supabase.table("teacher_attendance").update({
                    "status": status,
                    "remark": remark
                }).eq("id", existing.data[0]["id"]).execute()
            else:
                # Create new
                supabase.table("teacher_attendance").insert({
                    "student_id": student_id,
                    "teacher_id": current_user["id"],
                    "date": bulk_data.date,
                    "status": status,
                    "remark": remark
                }).execute()
            
            success_count += 1
        
        return {
            "message": f"Bulk attendance completed! ({success_count} records updated, {fail_count} failed)",
            "success_count": success_count,
            "fail_count": fail_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process bulk attendance: {str(e)}")


# Student: Get My Attendance
@router.get("/student/attendance", response_model=List[AttendanceResponse])
async def get_student_attendance(
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("teacher_attendance").select("*, users(full_name as teacher_name)").eq("student_id", current_user["id"]).order("date", desc=True).execute()
        
        # Get student details
        student = supabase.table("students").select("*").eq("id", current_user["id"]).execute()
        
        return [
            AttendanceResponse(
                id=a["id"],
                student_id=a["student_id"],
                student_name=student.data[0]["full_name"],
                admission_no=student.data[0]["admission_no"],
                student_class=student.data[0]["class"],
                date=a["date"],
                status=a["status"],
                remark=a.get("remark")
            )
            for a in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch attendance: {str(e)}")


# Teacher: Get Attendance Summary by Date
@router.get("/teacher/attendance/summary")
async def get_attendance_summary(
    date: str,
    current_user = Depends(require_role(["teacher"]))
):
    supabase = get_supabase_client()
    
    # Get teacher's assigned classes
    teacher_result = supabase.table("users").select("assigned_classes").eq("id", current_user["id"]).execute()
    assigned_classes = teacher_result.data[0].get("assigned_classes", "")
    class_list = [c.strip() for c in assigned_classes.split(',') if c.strip()]
    
    try:
        # Get all students in assigned classes
        if not class_list or "all" in assigned_classes:
            students = supabase.table("students").select("*").execute()
        else:
            students = supabase.table("students").select("*").in_("class", class_list).execute()
        
        total_students = len(students.data)
        
        # Get attendance for this date
        attendance = supabase.table("teacher_attendance").select("*").eq("teacher_id", current_user["id"]).eq("date", date).execute()
        
        present_count = sum(1 for a in attendance.data if a["status"] == "present")
        absent_count = sum(1 for a in attendance.data if a["status"] == "absent")
        late_count = sum(1 for a in attendance.data if a["status"] == "late")
        
        return {
            "date": date,
            "total_students": total_students,
            "present": present_count,
            "absent": absent_count,
            "late": late_count,
            "not_marked": total_students - len(attendance.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch attendance summary: {str(e)}")

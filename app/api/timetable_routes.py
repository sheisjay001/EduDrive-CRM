from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel

from app.core.auth import get_current_user, require_role
from app.database.session import get_supabase_client

router = APIRouter()


# Pydantic Models
class TimetableCreate(BaseModel):
    title: str
    session: str
    term: str
    type: str = "class"  # exam, class, general
    student_class: str = "all"


class TimetableResponse(BaseModel):
    id: int
    title: str
    file_path: str
    type: str
    student_class: str
    session: str
    term: str
    uploaded_at: str


# Admin: Upload Timetable
@router.post("/timetables", response_model=TimetableResponse)
async def upload_timetable(
    title: str,
    session: str,
    term: str,
    type: str = "class",
    student_class: str = "all",
    file: UploadFile = File(...),
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    # Validate file type
    allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
    file_extension = file.filename.split('.')[-1].lower() if file.filename else ''
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, JPG, PNG allowed")
    
    # Generate unique filename
    import time
    unique_filename = f"{int(time.time())}_{file.filename}"
    
    # In a real implementation, you would upload to a storage service (S3, Supabase Storage, etc.)
    # For now, we'll store the filename
    file_path = f"uploads/timetables/{unique_filename}"
    
    try:
        result = supabase.table("timetables").insert({
            "title": title,
            "file_path": file_path,
            "type": type,
            "class": student_class,
            "session": session,
            "term": term,
            "uploaded_by": current_user["id"]
        }).execute()
        
        return TimetableResponse(
            id=result.data[0]["id"],
            title=result.data[0]["title"],
            file_path=result.data[0]["file_path"],
            type=result.data[0]["type"],
            student_class=result.data[0]["class"],
            session=result.data[0]["session"],
            term=result.data[0]["term"],
            uploaded_at=result.data[0]["uploaded_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload timetable: {str(e)}")


# Admin: Get All Timetables
@router.get("/timetables", response_model=List[TimetableResponse])
async def get_all_timetables(
    current_user = Depends(require_role(["admin", "super_admin", "school_admin", "teacher"]))
):
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("timetables").select("*").order("uploaded_at", desc=True).execute()
        
        return [
            TimetableResponse(
                id=tt["id"],
                title=tt["title"],
                file_path=tt["file_path"],
                type=tt["type"],
                student_class=tt["class"],
                session=tt["session"],
                term=tt["term"],
                uploaded_at=tt["uploaded_at"]
            )
            for tt in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch timetables: {str(e)}")


# Admin: Delete Timetable
@router.delete("/timetables/{timetable_id}")
async def delete_timetable(
    timetable_id: int,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        # In a real implementation, you would also delete the file from storage
        supabase.table("timetables").delete().eq("id", timetable_id).execute()
        return {"message": "Timetable deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete timetable: {str(e)}")


# Student: Get Timetables for Class
@router.get("/timetables/my-class", response_model=List[TimetableResponse])
async def get_my_class_timetables(
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    # Get student's class
    student_result = supabase.table("students").select("class").eq("id", current_user["id"]).execute()
    if not student_result.data:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_class = student_result.data[0]["class"]
    
    try:
        result = supabase.table("timetables").select("*").or_(f"class.eq.{student_class},class.eq.all").order("uploaded_at", desc=True).execute()
        
        return [
            TimetableResponse(
                id=tt["id"],
                title=tt["title"],
                file_path=tt["file_path"],
                type=tt["type"],
                student_class=tt["class"],
                session=tt["session"],
                term=tt["term"],
                uploaded_at=tt["uploaded_at"]
            )
            for tt in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch timetables: {str(e)}")


# Teacher: Get Timetables for Assigned Classes
@router.get("/timetables/teacher", response_model=List[TimetableResponse])
async def get_teacher_timetables(
    current_user = Depends(require_role(["teacher"]))
):
    supabase = get_supabase_client()
    
    # Get teacher's assigned classes
    teacher_result = supabase.table("users").select("assigned_classes").eq("id", current_user["id"]).execute()
    if not teacher_result.data:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    assigned_classes = teacher_result.data[0].get("assigned_classes", "")
    if not assigned_classes:
        # Return all timetables if no classes assigned
        assigned_classes = "all"
    
    class_list = [c.strip() for c in assigned_classes.split(',') if c.strip()]
    
    try:
        if "all" in assigned_classes or not class_list:
            result = supabase.table("timetables").select("*").order("uploaded_at", desc=True).execute()
        else:
            # Build OR query for multiple classes
            filters = [f"class.eq.{c}" for c in class_list]
            filters.append("class.eq.all")
            or_filter = ",".join(filters)
            result = supabase.table("timetables").select("*").or_(or_filter).order("uploaded_at", desc=True).execute()
        
        return [
            TimetableResponse(
                id=tt["id"],
                title=tt["title"],
                file_path=tt["file_path"],
                type=tt["type"],
                student_class=tt["class"],
                session=tt["session"],
                term=tt["term"],
                uploaded_at=tt["uploaded_at"]
            )
            for tt in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch timetables: {str(e)}")

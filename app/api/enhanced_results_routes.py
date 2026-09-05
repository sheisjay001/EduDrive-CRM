from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import get_current_user, require_role
from app.database.session import get_supabase_client

router = APIRouter()


# Pydantic Models
class ResultCheckRequest(BaseModel):
    session: str
    term: str
    pin_code: str
    serial_number: str


class ResultCreate(BaseModel):
    student_id: int
    subject: str
    ca_score: float = 0
    exam_score: float = 0
    term: str
    session: str


class ResultUpdate(BaseModel):
    ca_score: float
    exam_score: float


class ResultResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    admission_no: str
    subject: str
    ca_score: float
    exam_score: float
    score: float
    term: str
    session: str
    student_class: str


# Student: Check Results with PIN Verification
@router.post("/results/check", response_model=List[ResultResponse])
async def check_results_with_pin(
    request: ResultCheckRequest,
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    # Clean PIN input
    pin_code = request.pin_code.replace(' ', '').replace('-', '')
    serial_number = request.serial_number.strip()
    
    # Verify PIN
    pin_result = supabase.table("pins").select("*").eq("pin_code", pin_code).eq("serial_number", serial_number).execute()
    
    if not pin_result.data:
        raise HTTPException(status_code=400, detail="Invalid Scratch Card PIN or Serial Number")
    
    pin_data = pin_result.data[0]
    
    # Check PIN status
    if pin_data["status"] == "blocked":
        raise HTTPException(status_code=400, detail="This PIN has been blocked")
    
    # Process PIN usage
    allow_access = False
    if pin_data["status"] == "unused":
        # Bind PIN to student
        supabase.table("pins").update({
            "status": "used",
            "student_id": current_user["id"],
            "usage_count": 1,
            "used_at": datetime.now().isoformat()
        }).eq("id", pin_data["id"]).execute()
        allow_access = True
    elif pin_data["status"] == "used":
        if pin_data["student_id"] == current_user["id"]:
            if pin_data["usage_count"] < pin_data["max_usage"]:
                supabase.table("pins").update({
                    "usage_count": pin_data["usage_count"] + 1
                }).eq("id", pin_data["id"]).execute()
                allow_access = True
            else:
                raise HTTPException(status_code=400, detail=f"PIN usage limit exceeded (Max {pin_data['max_usage']} uses)")
        else:
            raise HTTPException(status_code=400, detail="This PIN is already used by another student")
    
    if not allow_access:
        raise HTTPException(status_code=400, detail="PIN verification failed")
    
    # Fetch results
    try:
        result = supabase.table("results").select("*, students(full_name, admission_no, class)").eq("student_id", current_user["id"]).eq("term", request.term).eq("session", request.session).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail=f"No results found for {request.term} {request.session}")
        
        return [
            ResultResponse(
                id=r["id"],
                student_id=r["student_id"],
                student_name=r["students"]["full_name"],
                admission_no=r["students"]["admission_no"],
                subject=r["subject"],
                ca_score=r.get("ca_score", 0),
                exam_score=r.get("exam_score", 0),
                score=r["score"],
                term=r["term"],
                session=r["session"],
                student_class=r["students"]["class"]
            )
            for r in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")


# Admin: Get All Results with Filters
@router.get("/results", response_model=List[ResultResponse])
async def get_all_results(
    filter_class: Optional[str] = None,
    filter_subject: Optional[str] = None,
    filter_term: Optional[str] = None,
    filter_session: Optional[str] = None,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin", "teacher"]))
):
    supabase = get_supabase_client()
    
    try:
        query = supabase.table("results").select("*, students(full_name, admission_no, class)")
        
        if filter_class:
            query = query.filter("students.class", "eq", filter_class)
        if filter_subject:
            query = query.eq("subject", filter_subject)
        if filter_term:
            query = query.eq("term", filter_term)
        if filter_session:
            query = query.eq("session", filter_session)
        
        result = query.order("id", desc=True).limit(100).execute()
        
        return [
            ResultResponse(
                id=r["id"],
                student_id=r["student_id"],
                student_name=r["students"]["full_name"],
                admission_no=r["students"]["admission_no"],
                subject=r["subject"],
                ca_score=r.get("ca_score", 0),
                exam_score=r.get("exam_score", 0),
                score=r["score"],
                term=r["term"],
                session=r["session"],
                student_class=r["students"]["class"]
            )
            for r in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")


# Admin/Teacher: Create Result
@router.post("/results", response_model=ResultResponse)
async def create_result(
    result_data: ResultCreate,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin", "teacher"]))
):
    supabase = get_supabase_client()
    
    total_score = result_data.ca_score + result_data.exam_score
    
    try:
        # Check if result already exists
        existing = supabase.table("results").select("*").eq("student_id", result_data.student_id).eq("subject", result_data.subject).eq("term", result_data.term).eq("session", result_data.session).execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Result already exists for this student, subject, term, and session")
        
        result = supabase.table("results").insert({
            "student_id": result_data.student_id,
            "subject": result_data.subject,
            "ca_score": result_data.ca_score,
            "exam_score": result_data.exam_score,
            "score": total_score,
            "term": result_data.term,
            "session": result_data.session,
            "uploaded_by": current_user["id"],
            "uploaded_at": datetime.now().isoformat()
        }).execute()
        
        # Fetch student details for response
        student = supabase.table("students").select("*").eq("id", result_data.student_id).execute()
        
        return ResultResponse(
            id=result.data[0]["id"],
            student_id=result.data[0]["student_id"],
            student_name=student.data[0]["full_name"],
            admission_no=student.data[0]["admission_no"],
            subject=result.data[0]["subject"],
            ca_score=result.data[0]["ca_score"],
            exam_score=result.data[0]["exam_score"],
            score=result.data[0]["score"],
            term=result.data[0]["term"],
            session=result.data[0]["session"],
            student_class=student.data[0]["class"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create result: {str(e)}")


# Admin/Teacher: Update Result
@router.put("/results/{result_id}", response_model=ResultResponse)
async def update_result(
    result_id: int,
    result_data: ResultUpdate,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin", "teacher"]))
):
    supabase = get_supabase_client()
    
    total_score = result_data.ca_score + result_data.exam_score
    
    try:
        result = supabase.table("results").update({
            "ca_score": result_data.ca_score,
            "exam_score": result_data.exam_score,
            "score": total_score
        }).eq("id", result_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Fetch student details for response
        student = supabase.table("students").select("*").eq("id", result.data[0]["student_id"]).execute()
        
        return ResultResponse(
            id=result.data[0]["id"],
            student_id=result.data[0]["student_id"],
            student_name=student.data[0]["full_name"],
            admission_no=student.data[0]["admission_no"],
            subject=result.data[0]["subject"],
            ca_score=result.data[0]["ca_score"],
            exam_score=result.data[0]["exam_score"],
            score=result.data[0]["score"],
            term=result.data[0]["term"],
            session=result.data[0]["session"],
            student_class=student.data[0]["class"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update result: {str(e)}")


# Admin: Delete Result
@router.delete("/results/{result_id}")
async def delete_result(
    result_id: int,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        supabase.table("results").delete().eq("id", result_id).execute()
        return {"message": "Result deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete result: {str(e)}")


# Teacher: Get Results for Assigned Classes
@router.get("/results/teacher", response_model=List[ResultResponse])
async def get_teacher_results(
    filter_term: Optional[str] = None,
    filter_session: Optional[str] = None,
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
            # Get all results
            query = supabase.table("results").select("*, students(full_name, admission_no, class)")
        else:
            # Get results for assigned classes
            query = supabase.table("results").select("*, students(full_name, admission_no, class)").in_("students.class", class_list)
        
        if filter_term:
            query = query.eq("term", filter_term)
        if filter_session:
            query = query.eq("session", filter_session)
        
        result = query.order("id", desc=True).limit(100).execute()
        
        return [
            ResultResponse(
                id=r["id"],
                student_id=r["student_id"],
                student_name=r["students"]["full_name"],
                admission_no=r["students"]["admission_no"],
                subject=r["subject"],
                ca_score=r.get("ca_score", 0),
                exam_score=r.get("exam_score", 0),
                score=r["score"],
                term=r["term"],
                session=r["session"],
                student_class=r["students"]["class"]
            )
            for r in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")


# Teacher: Upload Results via CSV
@router.post("/results/upload-csv")
async def upload_results_csv(
    term: str,
    session: str,
    subject: str,
    file_content: str,
    current_user = Depends(require_role(["teacher"]))
):
    supabase = get_supabase_client()
    
    import io
    import csv
    
    try:
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(file_content))
        
        success_count = 0
        fail_count = 0
        
        for row in csv_reader:
            admission_no = row.get("Admission No", "").strip()
            ca_score = float(row.get("CA Score", 0))
            exam_score = float(row.get("Exam Score", 0))
            total_score = ca_score + exam_score
            
            if not admission_no:
                fail_count += 1
                continue
            
            # Find student by admission number
            student = supabase.table("students").select("*").eq("admission_no", admission_no).execute()
            
            if not student.data:
                fail_count += 1
                continue
            
            student_id = student.data[0]["id"]
            
            # Check if result exists
            existing = supabase.table("results").select("*").eq("student_id", student_id).eq("subject", subject).eq("term", term).eq("session", session).execute()
            
            if existing.data:
                # Update
                supabase.table("results").update({
                    "ca_score": ca_score,
                    "exam_score": exam_score,
                    "score": total_score,
                    "uploaded_by": current_user["id"],
                    "uploaded_at": datetime.now().isoformat()
                }).eq("id", existing.data[0]["id"]).execute()
            else:
                # Insert
                supabase.table("results").insert({
                    "student_id": student_id,
                    "subject": subject,
                    "ca_score": ca_score,
                    "exam_score": exam_score,
                    "score": total_score,
                    "term": term,
                    "session": session,
                    "uploaded_by": current_user["id"],
                    "uploaded_at": datetime.now().isoformat()
                }).execute()
            
            success_count += 1
        
        return {
            "message": f"Results uploaded successfully! ({success_count} records updated, {fail_count} failed/not found)",
            "success_count": success_count,
            "fail_count": fail_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload CSV: {str(e)}")

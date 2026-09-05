from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import get_current_user, require_role
from app.database.session import get_supabase_client

router = APIRouter()


# Pydantic Models
class CBTExamCreate(BaseModel):
    title: str
    student_class: str
    duration_minutes: int = 30
    status: str = "active"


class CBTQuestionCreate(BaseModel):
    exam_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str


class CBTExamResponse(BaseModel):
    id: int
    title: str
    student_class: str
    duration_minutes: int
    status: str
    created_at: str


class CBTQuestionResponse(BaseModel):
    id: int
    exam_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str


class CBTResultSubmit(BaseModel):
    exam_id: int
    answers: dict  # question_id: selected_option


class CBTResultResponse(BaseModel):
    id: int
    exam_id: int
    score: int
    total_questions: int
    date_taken: str


# Admin: Create CBT Exam
@router.post("/cbt/exams", response_model=CBTExamResponse)
async def create_cbt_exam(
    exam_data: CBTExamCreate,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("cbt_exams").insert({
            "title": exam_data.title,
            "class": exam_data.student_class,
            "duration_minutes": exam_data.duration_minutes,
            "status": exam_data.status,
            "created_by": current_user["id"]
        }).execute()
        
        return CBTExamResponse(
            id=result.data[0]["id"],
            title=result.data[0]["title"],
            student_class=result.data[0]["class"],
            duration_minutes=result.data[0]["duration_minutes"],
            status=result.data[0]["status"],
            created_at=result.data[0]["created_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create exam: {str(e)}")


# Admin: Add Question to Exam
@router.post("/cbt/questions", response_model=CBTQuestionResponse)
async def add_cbt_question(
    question_data: CBTQuestionCreate,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    # Validate correct_option
    if question_data.correct_option not in ['a', 'b', 'c', 'd']:
        raise HTTPException(status_code=400, detail="Correct option must be a, b, c, or d")
    
    try:
        result = supabase.table("cbt_questions").insert({
            "exam_id": question_data.exam_id,
            "question_text": question_data.question_text,
            "option_a": question_data.option_a,
            "option_b": question_data.option_b,
            "option_c": question_data.option_c,
            "option_d": question_data.option_d,
            "correct_option": question_data.correct_option
        }).execute()
        
        return CBTQuestionResponse(
            id=result.data[0]["id"],
            exam_id=result.data[0]["exam_id"],
            question_text=result.data[0]["question_text"],
            option_a=result.data[0]["option_a"],
            option_b=result.data[0]["option_b"],
            option_c=result.data[0]["option_c"],
            option_d=result.data[0]["option_d"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add question: {str(e)}")


# Admin: Get All Exams
@router.get("/cbt/exams", response_model=List[CBTExamResponse])
async def get_all_cbt_exams(
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("cbt_exams").select("*").order("id", desc=True).execute()
        
        return [
            CBTExamResponse(
                id=exam["id"],
                title=exam["title"],
                student_class=exam["class"],
                duration_minutes=exam["duration_minutes"],
                status=exam["status"],
                created_at=exam["created_at"]
            )
            for exam in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch exams: {str(e)}")


# Admin: Delete Exam
@router.delete("/cbt/exams/{exam_id}")
async def delete_cbt_exam(
    exam_id: int,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        supabase.table("cbt_exams").delete().eq("id", exam_id).execute()
        return {"message": "Exam deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete exam: {str(e)}")


# Admin: Update CBT Exam
@router.patch("/cbt/exams/{exam_id}")
async def update_cbt_exam(
    exam_id: int,
    payload: dict,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))):
    supabase = get_supabase_client()
    
    try:
        update_data: dict = {}
        if payload.get("title") is not None:
            update_data["title"] = payload["title"]
        if payload.get("class") is not None:
            update_data["class"] = payload["class"]
        elif payload.get("student_class") is not None:
            update_data["class"] = payload["student_class"]
        if payload.get("duration_minutes") is not None:
            update_data["duration_minutes"] = payload["duration_minutes"]
        if payload.get("status") is not None:
            update_data["status"] = payload["status"]
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        result = supabase.table("cbt_exams").update(update_data).eq("id", exam_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        updated = result.data[0]
        return CBTExamResponse(
            id=updated["id"],
            title=updated["title"],
            student_class=updated["class"],
            duration_minutes=updated["duration_minutes"],
            status=updated["status"],
            created_at=updated["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update exam: {str(e)}")


# Student: Get Active Exams for Class
@router.get("/cbt/exams/active", response_model=List[CBTExamResponse])
async def get_active_exams_for_student(
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    # Get student's class
    student_result = supabase.table("students").select("class").eq("id", current_user["id"]).execute()
    if not student_result.data:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_class = student_result.data[0]["class"]
    
    try:
        result = supabase.table("cbt_exams").select("*").eq("class", student_class).eq("status", "active").execute()
        
        return [
            CBTExamResponse(
                id=exam["id"],
                title=exam["title"],
                student_class=exam["class"],
                duration_minutes=exam["duration_minutes"],
                status=exam["status"],
                created_at=exam["created_at"]
            )
            for exam in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch active exams: {str(e)}")


# Student: Get Exam Questions (without correct answers)
@router.get("/cbt/exams/{exam_id}/questions")
async def get_exam_questions(
    exam_id: int,
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("cbt_questions").select("id, question_text, option_a, option_b, option_c, option_d").eq("exam_id", exam_id).execute()
        
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch questions: {str(e)}")


# Student: Submit CBT Result
@router.post("/cbt/results", response_model=CBTResultResponse)
async def submit_cbt_result(
    result_data: CBTResultSubmit,
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    # Get questions and correct answers
    questions_result = supabase.table("cbt_questions").select("*").eq("exam_id", result_data.exam_id).execute()
    questions = questions_result.data
    
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this exam")
    
    # Calculate score
    score = 0
    for question in questions:
        question_id = question["id"]
        correct_option = question["correct_option"]
        selected_option = result_data.answers.get(str(question_id))
        
        if selected_option == correct_option:
            score += 1
    
    # Check if student already took this exam
    existing_result = supabase.table("cbt_results").select("*").eq("exam_id", result_data.exam_id).eq("student_id", current_user["id"]).execute()
    
    try:
        if existing_result.data:
            # Update existing result
            result = supabase.table("cbt_results").update({
                "score": score,
                "total_questions": len(questions),
                "date_taken": datetime.now().isoformat()
            }).eq("id", existing_result.data[0]["id"]).execute()
            
            return CBTResultResponse(
                id=result.data[0]["id"],
                exam_id=result.data[0]["exam_id"],
                score=result.data[0]["score"],
                total_questions=result.data[0]["total_questions"],
                date_taken=result.data[0]["date_taken"]
            )
        else:
            # Insert new result
            result = supabase.table("cbt_results").insert({
                "exam_id": result_data.exam_id,
                "student_id": current_user["id"],
                "score": score,
                "total_questions": len(questions),
                "date_taken": datetime.now().isoformat()
            }).execute()
            
            return CBTResultResponse(
                id=result.data[0]["id"],
                exam_id=result.data[0]["exam_id"],
                score=result.data[0]["score"],
                total_questions=result.data[0]["total_questions"],
                date_taken=result.data[0]["date_taken"]
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit result: {str(e)}")


# Student: Get CBT History
@router.get("/cbt/results/history", response_model=List[CBTResultResponse])
async def get_cbt_history(
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("cbt_results").select("*, cbt_exams(title)").eq("student_id", current_user["id"]).order("date_taken", desc=True).execute()
        
        return [
            CBTResultResponse(
                id=r["id"],
                exam_id=r["exam_id"],
                score=r["score"],
                total_questions=r["total_questions"],
                date_taken=r["date_taken"]
            )
            for r in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.auth import get_current_user, require_role
from app.database.session import get_supabase_client

router = APIRouter()


# Pydantic Models
class NotificationCreate(BaseModel):
    title: str
    message: str
    target_audience: str = "all"  # all, student, teacher, parent, admin


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    target_audience: str
    created_at: str


# Admin: Create Notification
@router.post("/notifications", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    if not notification_data.title or not notification_data.message:
        raise HTTPException(status_code=400, detail="Title and message are required")
    
    try:
        result = supabase.table("notifications").insert({
            "title": notification_data.title,
            "message": notification_data.message,
            "target_audience": notification_data.target_audience,
            "created_by": current_user["id"]
        }).execute()
        
        return NotificationResponse(
            id=result.data[0]["id"],
            title=result.data[0]["title"],
            message=result.data[0]["message"],
            target_audience=result.data[0]["target_audience"],
            created_at=result.data[0]["created_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create notification: {str(e)}")


# Admin: Get All Notifications
@router.get("/notifications", response_model=List[NotificationResponse])
async def get_all_notifications(
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("notifications").select("*").order("created_at", desc=True).execute()
        
        return [
            NotificationResponse(
                id=n["id"],
                title=n["title"],
                message=n["message"],
                target_audience=n["target_audience"],
                created_at=n["created_at"]
            )
            for n in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


# Admin: Delete Notification
@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user = Depends(require_role(["admin", "super_admin", "school_admin"]))
):
    supabase = get_supabase_client()
    
    try:
        supabase.table("notifications").delete().eq("id", notification_id).execute()
        return {"message": "Notification deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")


# Student: Get Notifications for Students
@router.get("/notifications/student", response_model=List[NotificationResponse])
async def get_student_notifications(
    current_user = Depends(require_role(["student"]))
):
    supabase = get_supabase_client()
    
    try:
        # Get notifications targeted at 'all' or 'student'
        result = supabase.table("notifications").select("*").in_("target_audience", ["all", "student"]).order("created_at", desc=True).execute()
        
        return [
            NotificationResponse(
                id=n["id"],
                title=n["title"],
                message=n["message"],
                target_audience=n["target_audience"],
                created_at=n["created_at"]
            )
            for n in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


# Teacher: Get Notifications for Teachers
@router.get("/notifications/teacher", response_model=List[NotificationResponse])
async def get_teacher_notifications(
    current_user = Depends(require_role(["teacher"]))
):
    supabase = get_supabase_client()
    
    try:
        # Get notifications targeted at 'all' or 'teacher'
        result = supabase.table("notifications").select("*").in_("target_audience", ["all", "teacher"]).order("created_at", desc=True).execute()
        
        return [
            NotificationResponse(
                id=n["id"],
                title=n["title"],
                message=n["message"],
                target_audience=n["target_audience"],
                created_at=n["created_at"]
            )
            for n in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


# Parent: Get Notifications for Parents
@router.get("/notifications/parent", response_model=List[NotificationResponse])
async def get_parent_notifications(
    current_user = Depends(require_role(["parent"]))
):
    supabase = get_supabase_client()
    
    try:
        # Get notifications targeted at 'all' or 'parent'
        result = supabase.table("notifications").select("*").in_("target_audience", ["all", "parent"]).order("created_at", desc=True).execute()
        
        return [
            NotificationResponse(
                id=n["id"],
                title=n["title"],
                message=n["message"],
                target_audience=n["target_audience"],
                created_at=n["created_at"]
            )
            for n in result.data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")

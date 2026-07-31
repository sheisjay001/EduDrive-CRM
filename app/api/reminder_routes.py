from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/reminders", tags=["reminders"])

class ReminderCreateRequest(BaseModel):
    reminder_type: str
    entity_type: str
    entity_id: str
    scheduled_for: datetime
    recipient_type: str
    recipient_contact: str
    channel: str
    subject: Optional[str]
    message_content: str
    template_id: Optional[str]

class ReminderResponse(BaseModel):
    id: str
    reminder_type: str
    entity_type: str
    entity_id: str
    scheduled_for: datetime
    status: str
    recipient_type: str
    recipient_contact: str
    channel: str
    subject: Optional[str]
    message_content: str
    sent_at: Optional[datetime]

@router.post("/create")
async def create_reminder(
    request: ReminderCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new reminder"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('reminders').insert({
            'reminder_type': request.reminder_type,
            'entity_type': request.entity_type,
            'entity_id': request.entity_id,
            'scheduled_for': request.scheduled_for.isoformat(),
            'status': 'pending',
            'recipient_type': request.recipient_type,
            'recipient_contact': request.recipient_contact,
            'channel': request.channel,
            'subject': request.subject,
            'message_content': request.message_content,
            'template_id': request.template_id,
            'school_id': current_user.schoolId,
            'created_by': current_user.id
        }).execute()
        
        return {"success": True, "reminder_id": result.data[0]['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lead-followup/{lead_id}")
async def create_lead_followup(
    lead_id: str,
    lead_stage: str,
    parent_contact: str,
    parent_name: str,
    child_name: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create automatic follow-up reminder for a lead"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('create_lead_followup_reminder', {
            'p_lead_id': lead_id,
            'p_lead_stage': lead_stage,
            'p_parent_contact': parent_contact,
            'p_parent_name': parent_name,
            'p_child_name': child_name,
            'p_school_id': current_user.schoolId,
            'p_created_by': current_user.id
        }).execute()
        
        return {"success": True, "reminder_id": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payment-reminder/{invoice_id}")
async def create_payment_reminder(
    invoice_id: str,
    parent_contact: str,
    parent_name: str,
    student_name: str,
    amount: str,
    due_date: str,
    days_offset: int,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create payment reminder for an invoice"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('create_payment_reminder', {
            'p_invoice_id': invoice_id,
            'p_parent_contact': parent_contact,
            'p_parent_name': parent_name,
            'p_student_name': student_name,
            'p_amount': amount,
            'p_due_date': due_date,
            'p_days_offset': days_offset,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "reminder_id": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending")
async def get_pending_reminders(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all pending reminders that are due"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('reminders').select('*')\
            .eq('status', 'pending')\
            .lte('scheduled_for', datetime.now().isoformat())\
            .order('scheduled_for', asc=True)\
            .execute()
        
        return {"reminders": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_reminders(
    entity_type: str,
    entity_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all reminders for a specific entity"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('reminders').select('*')\
            .eq('entity_type', entity_type)\
            .eq('entity_id', entity_id)\
            .order('scheduled_for', desc=True)\
            .execute()
        
        return {"reminders": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{reminder_id}/send")
async def mark_reminder_sent(
    reminder_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Mark a reminder as sent"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('reminders').update({
            'status': 'sent',
            'sent_at': datetime.now().isoformat()
        }).eq('id', reminder_id).execute()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{reminder_id}/fail")
async def mark_reminder_failed(
    reminder_id: str,
    error_message: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Mark a reminder as failed"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('reminders').update({
            'status': 'failed',
            'error_message': error_message,
            'retry_count': 1
        }).eq('id', reminder_id).execute()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

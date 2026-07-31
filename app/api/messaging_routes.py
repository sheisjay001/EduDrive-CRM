from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import httpx
from app.core.auth import get_current_user, AuthUser
from app.core.config import settings

router = APIRouter(prefix="/messaging", tags=["messaging"])

class MessageTemplateCreateRequest(BaseModel):
    template_name: str
    template_code: str
    channel: str  # 'whatsapp', 'sms', 'email'
    use_case: str
    subject: Optional[str]
    body: str
    variables: Optional[List[str]]

class SendMessageRequest(BaseModel):
    recipient_type: str  # 'parent', 'staff', 'student'
    recipient_id: Optional[str]
    recipient_contact: str
    channel: str  # 'whatsapp', 'sms', 'email'
    message_type: str
    subject: Optional[str]
    message_content: str
    template_id: Optional[str]
    priority: int = 5
    scheduled_for: Optional[datetime]

class BroadcastMessageRequest(BaseModel):
    audience: str  # 'all_parents', 'specific_class', 'outstanding_fees', etc.
    channel: str
    message_type: str
    subject: Optional[str]
    message_content: str
    template_id: Optional[str]
    scheduled_for: Optional[datetime]

@router.post("/templates")
async def create_template(
    request: MessageTemplateCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new message template"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('message_templates').insert({
            'template_name': request.template_name,
            'template_code': request.template_code,
            'channel': request.channel,
            'use_case': request.use_case,
            'subject': request.subject,
            'body': request.body,
            'variables': request.variables,
            'created_by': current_user.id,
            'school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "template_id": result.data[0]['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_templates(
    channel: Optional[str] = None,
    use_case: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get message templates"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('message_templates').select('*').eq('is_active', True)
        
        if channel:
            query = query.eq('channel', channel)
        if use_case:
            query = query.eq('use_case', use_case)
        
        result = query.order('created_at', desc=True).execute()
        
        return {"templates": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Queue a message for sending"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('queue_message', {
            'p_recipient_type': request.recipient_type,
            'p_recipient_id': request.recipient_id,
            'p_recipient_contact': request.recipient_contact,
            'p_channel': request.channel,
            'p_message_type': request.message_type,
            'p_subject': request.subject,
            'p_message_content': request.message_content,
            'p_template_id': request.template_id,
            'p_priority': request.priority,
            'p_scheduled_for': request.scheduled_for.isoformat() if request.scheduled_for else None,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "queue_id": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast")
async def broadcast_message(
    request: BroadcastMessageRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Send broadcast message to multiple recipients"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        # Get recipients based on audience
        recipients = []
        
        if request.audience == "all_parents":
            result = supabase.table('parents').select('id, phone, email').execute()
            recipients = result.data
        elif request.audience == "outstanding_fees":
            # Get parents with outstanding fees
            result = supabase.table('invoices').select('parent_id, parent_phone, parent_email')\
                .eq('status', 'overdue').execute()
            recipients = result.data
        # Add more audience types as needed
        
        # Queue messages for all recipients
        queue_ids = []
        for recipient in recipients:
            contact = recipient.get('phone') if request.channel == 'whatsapp' or request.channel == 'sms' else recipient.get('email')
            
            result = supabase.rpc('queue_message', {
                'p_recipient_type': 'parent',
                'p_recipient_id': recipient.get('id'),
                'p_recipient_contact': contact,
                'p_channel': request.channel,
                'p_message_type': request.message_type,
                'p_subject': request.subject,
                'p_message_content': request.message_content,
                'p_template_id': request.template_id,
                'p_priority': 5,
                'p_scheduled_for': request.scheduled_for.isoformat() if request.scheduled_for else None,
                'p_school_id': current_user.schoolId
            }).execute()
            
            queue_ids.append(result.data[0])
        
        return {"success": True, "queued_count": len(queue_ids), "queue_ids": queue_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue/pending")
async def get_pending_messages(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get pending messages in queue"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('pending_messages').select('*').execute()
        return {"messages": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process/{queue_id}")
async def process_message(
    queue_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Process a message from queue (send via API)"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        # Get message from queue
        result = supabase.table('message_queue').select('*').eq('id', queue_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message = result.data[0]
        
        # Send based on channel
        external_id = None
        status = "sent"
        error = None
        cost = 0.0
        
        if message['channel'] == 'whatsapp':
            # Integrate with Termii or Meta Cloud API
            external_id, status, error, cost = await send_whatsapp_message(message)
        elif message['channel'] == 'sms':
            # Integrate with SMS API
            external_id, status, error, cost = await send_sms_message(message)
        elif message['channel'] == 'email':
            # Integrate with email service
            external_id, status, error, cost = await send_email_message(message)
        
        # Record sent message
        supabase.rpc('record_sent_message', {
            'p_queue_id': queue_id,
            'p_external_message_id': external_id,
            'p_status': status,
            'p_error_message': error,
            'p_cost': cost
        }).execute()
        
        return {"success": True, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def send_whatsapp_message(message: dict):
    """Send WhatsApp message via Termii or Meta Cloud API"""
    termii_api_key = getattr(settings, 'termii_api_key', None)
    
    if not termii_api_key:
        return None, "failed", "Termii not configured", 0.0
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.termii.com/api/sms/send",
                json={
                    "to": message['recipient_contact'],
                    "from": "EduDrive",
                    "sms": message['message_content'],
                    "type": "plain",
                    "channel": "whatsapp"
                },
                headers={
                    "Authorization": f"Bearer {termii_api_key}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message_id'), "sent", None, data.get('cost', 0.0)
            else:
                return None, "failed", response.text, 0.0
        except Exception as e:
            return None, "failed", str(e), 0.0

async def send_sms_message(message: dict):
    """Send SMS message via Termii"""
    termii_api_key = getattr(settings, 'termii_api_key', None)
    
    if not termii_api_key:
        return None, "failed", "Termii not configured", 0.0
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.termii.com/api/sms/send",
                json={
                    "to": message['recipient_contact'],
                    "from": "EduDrive",
                    "sms": message['message_content'],
                    "type": "plain",
                    "channel": "dnd"
                },
                headers={
                    "Authorization": f"Bearer {termii_api_key}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message_id'), "sent", None, data.get('cost', 0.0)
            else:
                return None, "failed", response.text, 0.0
        except Exception as e:
            return None, "failed", str(e), 0.0

async def send_email_message(message: dict):
    """Send email message (placeholder for email integration)"""
    # This would integrate with SendGrid, Mailgun, or similar
    return None, "sent", None, 0.0

@router.get("/statistics")
async def get_messaging_statistics(
    days: int = Query(30, ge=1, le=365),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get messaging statistics"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('message_statistics').select('*').execute()
        return {"statistics": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sent")
async def get_sent_messages(
    recipient_type: Optional[str] = None,
    channel: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get sent messages history"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('sent_messages').select('*')
        
        if recipient_type:
            query = query.eq('recipient_type', recipient_type)
        if channel:
            query = query.eq('channel', channel)
        
        result = query.order('created_at', desc=True).limit(100).execute()
        
        return {"messages": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

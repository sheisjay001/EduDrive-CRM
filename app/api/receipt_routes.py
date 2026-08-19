from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/receipts", tags=["receipts"])

class ReceiptCreateRequest(BaseModel):
    payment_id: str
    invoice_id: Optional[str]
    student_id: Optional[str]
    parent_id: Optional[str]

class ReceiptDeliveryRequest(BaseModel):
    receipt_id: str
    delivery_method: str  # 'email', 'whatsapp', 'sms'

@router.post("/generate")
async def generate_receipt(
    request: ReceiptCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Generate a receipt for a payment"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        receipt_id = supabase.rpc('create_payment_receipt', {
            'p_payment_id': request.payment_id,
            'p_invoice_id': request.invoice_id,
            'p_student_id': request.student_id,
            'p_parent_id': request.parent_id,
            'p_issued_by': current_user.id,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "receipt_id": receipt_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/queue-delivery")
async def queue_receipt_delivery(
    request: ReceiptDeliveryRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Queue receipt for delivery"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        delivery_id = supabase.rpc('queue_receipt_delivery', {
            'p_receipt_id': request.receipt_id,
            'p_delivery_method': request.delivery_method,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "delivery_id": delivery_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
async def get_recent_receipts(
    limit: int = 50,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get recent receipts"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('recent_receipts').select('*').limit(limit).execute()
        return {"receipts": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{receipt_id}")
async def get_receipt(
    receipt_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get receipt details"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('receipts').select('*').eq('id', receipt_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        return {"receipt": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

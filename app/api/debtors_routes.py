from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/debtors", tags=["debtors"])

class DebtorsUpdateRequest(BaseModel):
    debtor_id: str
    collection_status: Optional[str]
    assigned_to: Optional[str]
    assigned_to_name: Optional[str]
    promise_to_pay_date: Optional[date]
    promise_amount: Optional[float]
    promise_kept: Optional[bool]
    notes: Optional[str]

class ReconciliationRequest(BaseModel):
    payment_id: str
    invoice_id: str
    notes: Optional[str]

@router.get("/summary")
async def get_debtors_summary(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get debtors summary by aging bucket"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('debtors_summary').select('*').execute()
        return {"summary": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/details")
async def get_debtor_details(
    aging_bucket: Optional[str] = None,
    limit: int = 100,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get detailed debtor information"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('debtor_details').select('*')
        
        if aging_bucket:
            query = query.eq('aging_bucket', aging_bucket)
        
        result = query.limit(limit).execute()
        return {"debtors": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collection-performance")
async def get_collection_performance(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get collection staff performance"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('collection_performance').select('*').execute()
        return {"performance": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/update")
async def update_debtor(
    request: DebtorsUpdateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Update debtor information"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        update_data = {}
        if request.collection_status:
            update_data['collection_status'] = request.collection_status
        if request.assigned_to:
            update_data['assigned_to'] = request.assigned_to
        if request.assigned_to_name:
            update_data['assigned_to_name'] = request.assigned_to_name
        if request.promise_to_pay_date:
            update_data['promise_to_pay_date'] = request.promise_to_pay_date.isoformat()
        if request.promise_amount:
            update_data['promise_amount'] = request.promise_amount
        if request.promise_kept is not None:
            update_data['promise_kept'] = request.promise_kept
        if request.notes:
            update_data['notes'] = request.notes
        
        result = supabase.table('debtor_aging').update(update_data).eq('id', request.debtor_id).execute()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reconcile")
async def reconcile_payment(
    request: ReconciliationRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Reconcile payment with invoice"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        reconciliation_id = supabase.rpc('reconcile_payment', {
            'p_payment_id': request.payment_id,
            'p_invoice_id': request.invoice_id,
            'p_reconciled_by': current_user.id,
            'p_reconciled_by_name': current_user.fullName,
            'p_notes': request.notes,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "reconciliation_id": reconciliation_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-aging/{invoice_id}")
async def update_aging(
    invoice_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Manually trigger aging update for an invoice"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        supabase.rpc('update_debtor_aging', {'p_invoice_id': invoice_id}).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

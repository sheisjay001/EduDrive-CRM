from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/bulk-billing", tags=["bulk-billing"])

class BulkBillingJobRequest(BaseModel):
    job_name: str
    job_type: str  # 'tuition', 'registration', 'custom'
    fee_structure_id: Optional[str]
    academic_year: Optional[str]
    term: Optional[str]
    class_filter: Optional[str]
    student_filter: Optional[dict]
    invoice_date: Optional[date]
    due_date: Optional[date]

class FeeStructureRequest(BaseModel):
    structure_name: str
    structure_type: str
    academic_year: Optional[str]
    term: Optional[str]
    class_level: Optional[str]
    amount: float
    currency: str = "NGN"
    due_date_offset: int = 30
    description: Optional[str]
    is_recurring: bool = False
    recurring_frequency: Optional[str]

@router.post("/fee-structures")
async def create_fee_structure(
    request: FeeStructureRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a fee structure for bulk billing"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('fee_structures').insert({
            'structure_name': request.structure_name,
            'structure_type': request.structure_type,
            'academic_year': request.academic_year,
            'term': request.term,
            'class_level': request.class_level,
            'amount': request.amount,
            'currency': request.currency,
            'due_date_offset': request.due_date_offset,
            'description': request.description,
            'is_recurring': request.is_recurring,
            'recurring_frequency': request.recurring_frequency,
            'school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "structure_id": result.data[0]['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fee-structures")
async def get_fee_structures(
    structure_type: Optional[str] = None,
    is_active: bool = True,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get fee structures"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('fee_structures').select('*').eq('is_active', is_active)
        
        if structure_type:
            query = query.eq('structure_type', structure_type)
        
        result = query.order('created_at', desc=True).execute()
        return {"structures": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs")
async def create_bulk_billing_job(
    request: BulkBillingJobRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a bulk billing job"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        job_id = supabase.rpc('create_bulk_billing_job', {
            'p_job_name': request.job_name,
            'p_job_type': request.job_type,
            'p_fee_structure_id': request.fee_structure_id,
            'p_academic_year': request.academic_year,
            'p_term': request.term,
            'p_class_filter': request.class_filter,
            'p_student_filter': request.student_filter,
            'p_invoice_date': request.invoice_date,
            'p_due_date': request.due_date,
            'p_started_by': current_user.id,
            'p_started_by_name': current_user.fullName,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "job_id": job_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/process")
async def process_bulk_billing_job(
    job_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Process a bulk billing job"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        supabase.rpc('process_bulk_billing_job', {'p_job_id': job_id}).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def get_bulk_billing_jobs(
    status: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get bulk billing job history"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('bulk_billing_history').select('*')
        
        if status:
            query = query.eq('status', status)
        
        result = query.execute()
        return {"jobs": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}/details")
async def get_job_details(
    job_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get details of a specific bulk billing job"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('bulk_billing_job_details').select('*').eq('job_id', job_id).execute()
        return {"details": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/lost-leads", tags=["lost-leads"])

class LostLeadRequest(BaseModel):
    lead_id: str
    reason_category: str
    reason_description: Optional[str]
    detailed_reason: Optional[str]
    lost_to_competitor: Optional[str]
    competitor_offer_details: Optional[str]
    price_sensitivity: Optional[str]
    budget_range: Optional[str]
    decision_timeline: Optional[str]
    follow_up_potential: bool = False
    follow_up_date: Optional[date]

@router.post("/mark-lost")
async def mark_lead_as_lost(
    request: LostLeadRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Mark a lead as lost with reason tracking"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        reason_id = supabase.rpc('mark_lead_as_lost', {
            'p_lead_id': request.lead_id,
            'p_reason_category': request.reason_category,
            'p_reason_description': request.reason_description,
            'p_detailed_reason': request.detailed_reason,
            'p_lost_to_competitor': request.lost_to_competitor,
            'p_competitor_offer_details': request.competitor_offer_details,
            'p_price_sensitivity': request.price_sensitivity,
            'p_budget_range': request.budget_range,
            'p_decision_timeline': request.decision_timeline,
            'p_follow_up_potential': request.follow_up_potential,
            'p_follow_up_date': request.follow_up_date,
            'p_recorded_by': current_user.id,
            'p_recorded_by_name': current_user.fullName,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "reason_id": reason_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reasons")
async def get_lost_reason_categories(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get predefined lost lead reason categories"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('get_lost_reason_categories').execute()
        return {"categories": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_lost_lead_analytics(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get lost lead analytics by category"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('lost_lead_analytics').select('*').execute()
        return {"analytics": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/competitor-analysis")
async def get_competitor_analysis(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get competitor analysis from lost leads"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('competitor_analysis').select('*').execute()
        return {"competitors": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_lost_lead_trends(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get lost lead trends over time"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('lost_lead_trends').select('*').execute()
        return {"trends": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

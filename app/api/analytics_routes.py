from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import date
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/analytics", tags=["analytics"])

class EnrollmentPredictionRequest(BaseModel):
    prediction_date: date
    prediction_period: str
    class_level: Optional[str]
    session_id: Optional[str]
    prediction_method: str = "moving_average"

class FeeForecastRequest(BaseModel):
    forecast_date: date
    forecast_period: str
    term_id: Optional[str]
    prediction_method: str = "linear_regression"

class RetentionPredictionRequest(BaseModel):
    student_id: str
    prediction_date: date
    prediction_period: str = "term"

@router.post("/enrollment/predict")
async def predict_enrollment(
    request: EnrollmentPredictionRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Generate enrollment prediction"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        prediction_id = supabase.rpc('generate_enrollment_prediction', {
            'p_prediction_date': request.prediction_date,
            'p_prediction_period': request.prediction_period,
            'p_class_level': request.class_level,
            'p_session_id': request.session_id,
            'p_prediction_method': request.prediction_method,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "prediction_id": prediction_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fee/forecast")
async def forecast_fees(
    request: FeeForecastRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Generate fee collection forecast"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        forecast_id = supabase.rpc('generate_fee_forecast', {
            'p_forecast_date': request.forecast_date,
            'p_forecast_period': request.forecast_period,
            'p_term_id': request.term_id,
            'p_prediction_method': request.prediction_method,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "forecast_id": forecast_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retention/predict")
async def predict_retention(
    request: RetentionPredictionRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Generate retention prediction for a student"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        prediction_id = supabase.rpc('generate_retention_prediction', {
            'p_student_id': request.student_id,
            'p_prediction_date': request.prediction_date,
            'p_prediction_period': request.prediction_period,
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "prediction_id": prediction_id.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/enrollment/forecast")
async def get_enrollment_forecast(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get enrollment forecast summary"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('enrollment_forecast_summary').select('*').execute()
        return {"forecast": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fee/forecast")
async def get_fee_forecast(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get fee forecast summary"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('fee_forecast_summary').select('*').execute()
        return {"forecast": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/retention/risk")
async def get_retention_risk_report(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get retention risk report"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('retention_risk_report').select('*').execute()
        return {"risk_report": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_analytics_dashboard(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get comprehensive analytics dashboard"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('analytics_dashboard').select('*').limit(1).execute()
        return {"dashboard": result.data[0] if result.data else {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

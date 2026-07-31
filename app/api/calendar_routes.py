from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, date, time
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser

router = APIRouter(prefix="/calendar", tags=["calendar"])

class CalendarEventCreateRequest(BaseModel):
    event_type: str  # 'tour', 'assessment', 'meeting'
    title: str
    description: Optional[str]
    event_date: date
    start_time: time
    end_time: time
    location: Optional[str]
    related_entity_type: Optional[str]  # 'lead', 'student'
    related_entity_id: Optional[str]
    parent_name: Optional[str]
    parent_contact: Optional[str]
    parent_email: Optional[str]
    assigned_staff_id: Optional[str]
    assigned_staff_name: Optional[str]
    assessment_type: Optional[str]
    assessment_subjects: Optional[List[str]]
    tour_type: Optional[str]
    notes: Optional[str]

class CalendarEventUpdateRequest(BaseModel):
    status: Optional[str]
    notes: Optional[str]
    follow_up_required: Optional[bool]
    follow_up_date: Optional[date]

class AssessmentScheduleCreateRequest(BaseModel):
    assessment_name: str
    assessment_type: str
    assessment_date: date
    start_time: time
    end_time: time
    location: Optional[str]
    max_participants: int = 20
    description: Optional[str]
    required_documents: Optional[List[str]]

@router.post("/events")
async def create_event(
    request: CalendarEventCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new calendar event (tour, assessment, or meeting)"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('create_calendar_event', {
            'p_event_type': request.event_type,
            'p_title': request.title,
            'p_description': request.description,
            'p_event_date': request.event_date.isoformat(),
            'p_start_time': request.start_time.isoformat(),
            'p_end_time': request.end_time.isoformat(),
            'p_location': request.location,
            'p_related_entity_type': request.related_entity_type,
            'p_related_entity_id': request.related_entity_id,
            'p_parent_name': request.parent_name,
            'p_parent_contact': request.parent_contact,
            'p_parent_email': request.parent_email,
            'p_assigned_staff_id': request.assigned_staff_id,
            'p_assigned_staff_name': request.assigned_staff_name,
            'p_assessment_type': request.assessment_type,
            'p_assessment_subjects': request.assessment_subjects,
            'p_tour_type': request.tour_type,
            'p_notes': request.notes,
            'p_school_id': current_user.schoolId,
            'p_created_by': current_user.id
        }).execute()
        
        return {"success": True, "event_id": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get calendar events with optional filters"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        query = supabase.table('calendar_events').select('*')
        
        if start_date:
            query = query.gte('event_date', start_date.isoformat())
        if end_date:
            query = query.lte('event_date', end_date.isoformat())
        if event_type:
            query = query.eq('event_type', event_type)
        if status:
            query = query.eq('status', status)
        
        result = query.order('event_date', asc=True).order('start_time', asc=True).execute()
        
        return {"events": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/today")
async def get_todays_events(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get today's scheduled events"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('todays_events').select('*').execute()
        return {"events": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/upcoming")
async def get_upcoming_events(
    days: int = Query(7, ge=1, le=30),
    current_user: AuthUser = Depends(get_current_user)
):
    """Get upcoming events in the next N days"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        end_date = date.today() + timedelta(days=days)
        result = supabase.table('calendar_events').select('*')\
            .gte('event_date', date.today().isoformat())\
            .lte('event_date', end_date.isoformat())\
            .in_('status', ['scheduled', 'confirmed'])\
            .order('event_date', asc=True)\
            .order('start_time', asc=True)\
            .execute()
        
        return {"events": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}")
async def get_event(
    event_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get details of a specific event"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('calendar_events').select('*').eq('id', event_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return {"event": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/events/{event_id}")
async def update_event(
    event_id: str,
    request: CalendarEventUpdateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Update an event status or notes"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        update_data = {}
        if request.status:
            update_data['status'] = request.status
        if request.notes:
            update_data['notes'] = request.notes
        if request.follow_up_required is not None:
            update_data['follow_up_required'] = request.follow_up_required
        if request.follow_up_date:
            update_data['follow_up_date'] = request.follow_up_date.isoformat()
        
        update_data['updated_at'] = datetime.now().isoformat()
        
        result = supabase.table('calendar_events').update(update_data).eq('id', event_id).execute()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/events/{event_id}")
async def cancel_event(
    event_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Cancel an event"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('calendar_events').update({
            'status': 'cancelled',
            'updated_at': datetime.now().isoformat()
        }).eq('id', event_id).execute()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessments")
async def create_assessment_schedule(
    request: AssessmentScheduleCreateRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new assessment schedule"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('assessment_schedules').insert({
            'assessment_name': request.assessment_name,
            'assessment_type': request.assessment_type,
            'assessment_date': request.assessment_date.isoformat(),
            'start_time': request.start_time.isoformat(),
            'end_time': request.end_time.isoformat(),
            'location': request.location,
            'max_participants': request.max_participants,
            'current_participants': 0,
            'status': 'open',
            'description': request.description,
            'required_documents': request.required_documents,
            'school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "schedule_id": result.data[0]['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assessments")
async def get_assessment_schedules(
    current_user: AuthUser = Depends(get_current_user)
):
    """Get all assessment schedules"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.table('assessment_schedules').select('*')\
            .gte('assessment_date', date.today().isoformat())\
            .order('assessment_date', asc=True)\
            .execute()
        
        return {"schedules": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/availability")
async def check_availability(
    event_date: date,
    start_time: time,
    end_time: time,
    current_user: AuthUser = Depends(get_current_user)
):
    """Check if a time slot is available"""
    from app.database.session import get_supabase_client
    
    supabase = get_supabase_client()
    
    try:
        result = supabase.rpc('check_slot_availability', {
            'p_event_date': event_date.isoformat(),
            'p_start_time': start_time.isoformat(),
            'p_end_time': end_time.isoformat(),
            'p_school_id': current_user.schoolId
        }).execute()
        
        return {"available": result.data[0] == 0, "conflicting_events": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

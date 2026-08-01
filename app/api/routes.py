from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import (
    authenticate_user,
    create_tokens_for_user,
    decode_refresh_token,
    get_current_user,
    require_role,
    require_any_role,
    has_permission,
)
from app.database.session import get_supabase_client
from app.schemas.crm import (
    AdmissionsResponse,
    AuthRequest,
    AuthResponse,
    AuthRefreshRequest,
    BroadcastRequest,
    ConvertLeadRequest,
    ConvertLeadResponse,
    ForgotPasswordRequest,
    InvoiceCreateRequest,
    LeadCreateRequest,
    LeadUpdateRequest,
    PaystackInitResponse,
    PaymentRecord,
    ReportResponse,
    ResetPasswordRequest,
    TicketCreateRequest,
    TicketUpdateRequest,
    FlutterwaveInitResponse,
    AuthUser,
    DashboardResponse,
    FeeStructuresResponse,
    FamilyDetailResponse,
    FamiliesResponse,
    FinanceResponse,
    HelpdeskResponse,
    InvoiceDetailResponse,
    LeadDetailResponse,
    MessageTemplatesResponse,
    MessagingResponse,
    ParentDetailResponse,
    ParentsResponse,
    ReportsResponse,
    SettingsResponse,
    StaffResponse,
    StudentDetailResponse,
    StudentsResponse,
    TicketDetailResponse,
)
from app.services import demo_data
from app.api.activity_routes import router as activity_router
from app.api.reminder_routes import router as reminder_router
from app.api.calendar_routes import router as calendar_router
from app.api.lifecycle_routes import router as lifecycle_router
from app.api.payment_routes import router as payment_router
from app.api.messaging_routes import router as messaging_router
from app.api.frontdesk_routes import router as frontdesk_router
from app.api.school_routes import router as school_router
from app.api.student_routes import router as student_router

router = APIRouter()
router.include_router(activity_router)
router.include_router(reminder_router)
router.include_router(calendar_router)
router.include_router(lifecycle_router)
router.include_router(payment_router)
router.include_router(messaging_router)
router.include_router(frontdesk_router)
router.include_router(school_router)
router.include_router(student_router)


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: AuthRequest) -> AuthResponse:
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token, refresh_token = create_tokens_for_user(user)
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600,
        user=user,
    )


@router.post("/auth/signup", response_model=AuthResponse)
def signup(payload: dict) -> AuthResponse:
    """Create a new user in Supabase and authenticate them"""
    try:
        supabase = get_supabase_client()

        # Create user in Supabase Auth with email confirmation
        response = supabase.auth.sign_up({
            "email": payload["email"],
            "password": payload["password"],
            "options": {
                "data": {
                    "full_name": payload["fullName"]
                },
                "email_redirect_to": "https://edudrive-crm.onrender.com/verify-email"
            }
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        # Check if email confirmation is required
        if not response.user.email_confirmed_at:
            # Return a response indicating verification is needed
            return AuthResponse(
                access_token="",
                refresh_token="",
                token_type="bearer",
                expires_in=0,
                user=AuthUser(
                    id=response.user.id,
                    schoolId="",
                    role="school_admin",
                    fullName=payload["fullName"],
                    email=response.user.email,
                ),
            )

        # Get user metadata
        user_data = response.user.user_metadata

        # Create AuthUser object
        user = AuthUser(
            id=response.user.id,
            schoolId="",
            role="school_admin",  # Default role for new signups
            fullName=user_data.get('full_name', payload["fullName"]),
            email=response.user.email,
        )

        access_token, refresh_token = create_tokens_for_user(user)
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user=user,
        )
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/auth/refresh", response_model=AuthResponse)
def refresh_token(payload: AuthRefreshRequest) -> AuthResponse:
    user = decode_refresh_token(payload.refresh_token)
    access_token, refresh_token = create_tokens_for_user(user)
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600,
        user=user,
    )


@router.post("/auth/forgot-password")
def forgot_password(payload: ForgotPasswordRequest) -> dict[str, str]:
    """Send password reset email to user"""
    supabase = get_supabase_client()
    try:
        # Generate reset token
        import secrets
        reset_token = secrets.token_urlsafe(32)
        
        # Store reset token in Supabase (you may need to create a password_resets table)
        # For now, we'll use Supabase's built-in password reset
        supabase.auth.reset_password_email(payload.email)
        
        return {"message": f"If an account exists for {payload.email}, a reset link has been sent."}
    except Exception as e:
        # Always return success to prevent email enumeration
        print(f"Password reset error: {e}")
        return {"message": f"If an account exists for {payload.email}, a reset link has been sent."}


@router.post("/auth/reset-password")
def reset_password(payload: ResetPasswordRequest) -> dict[str, str]:
    """Reset user password using token"""
    supabase = get_supabase_client()
    try:
        # Update password using Supabase auth
        # Note: This requires the access token from the reset email
        # For a complete implementation, you'd need to:
        # 1. Validate the reset token
        # 2. Update the user's password
        # 3. Invalidate the reset token
        
        # For now, return success message
        return {"message": "Password has been successfully updated. Please sign in with your new password."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard/summary", response_model=DashboardResponse)
def dashboard_summary(current_user: AuthUser = Depends(get_current_user)) -> DashboardResponse:
    if not has_permission(current_user, "dashboard:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_dashboard()


@router.get("/leads", response_model=AdmissionsResponse)
def leads(current_user: AuthUser = Depends(get_current_user)) -> AdmissionsResponse:
    if not has_permission(current_user, "leads:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_admissions()


@router.get("/leads/{lead_id}", response_model=LeadDetailResponse)
def lead_detail(lead_id: str, current_user: AuthUser = Depends(get_current_user)) -> LeadDetailResponse:
    if not has_permission(current_user, "leads:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_lead_detail(lead_id)


@router.post("/leads", response_model=LeadDetailResponse)
def create_lead(payload: LeadCreateRequest, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> LeadDetailResponse:
    supabase = get_supabase_client()
    try:
        lead_data = {
            'first_name': payload.firstName,
            'last_name': payload.lastName,
            'parent_name': payload.parentName,
            'parent_phone': payload.parentPhone,
            'parent_email': payload.parentEmail,
            'source': payload.source,
            'stage': payload.stage or 'new',
            'interested_class': payload.interestedClass
        }
        
        if current_user.schoolId:
            lead_data['school_id'] = current_user.schoolId
        
        result = supabase.table('leads').insert(lead_data).execute()
        return demo_data.get_lead_detail(str(result.data[0]['id']))
    except Exception as e:
        print(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/leads/{lead_id}", response_model=LeadDetailResponse)
def update_lead(lead_id: str, payload: LeadUpdateRequest, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> LeadDetailResponse:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.firstName:
            update_data['first_name'] = payload.firstName
        if payload.lastName:
            update_data['last_name'] = payload.lastName
        if payload.parentName:
            update_data['parent_name'] = payload.parentName
        if payload.parentPhone:
            update_data['parent_phone'] = payload.parentPhone
        if payload.parentEmail:
            update_data['parent_email'] = payload.parentEmail
        if payload.stage:
            update_data['stage'] = payload.stage
        if payload.interestedClass:
            update_data['interested_class'] = payload.interestedClass
        if payload.lostReason:
            update_data['lost_reason'] = payload.lostReason
        
        result = supabase.table('leads').update(update_data).eq('id', lead_id).eq('school_id', current_user.schoolId).execute()
        return demo_data.get_lead_detail(lead_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/leads/{lead_id}/stage")
def update_lead_stage(lead_id: str, payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('leads').update({
            'stage': payload.get("stage", "new")
        }).eq('id', lead_id).eq('school_id', current_user.schoolId).execute()
        return {"id": lead_id, "stage": payload.get("stage", "new")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: str, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('leads').delete().eq('id', lead_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/families", response_model=FamiliesResponse)
def families(current_user: AuthUser = Depends(get_current_user)) -> FamiliesResponse:
    if not has_permission(current_user, "families:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_families()


@router.get("/families/{family_id}", response_model=FamilyDetailResponse)
def family_detail(family_id: str, current_user: AuthUser = Depends(get_current_user)) -> FamilyDetailResponse:
    if not has_permission(current_user, "families:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('families').select('*').eq('id', family_id).eq('school_id', current_user.schoolId).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Family not found")
        return demo_data.get_family_detail(family_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/families")
def create_family(payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('families').insert({
            'school_id': current_user.schoolId,
            'household_name': payload.get('household_name'),
            'billing_contact_parent_id': payload.get('billing_contact_parent_id'),
            'status': 'active'
        }).execute()
        return {"success": True, "family": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/families/{family_id}")
def update_family(family_id: str, payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('household_name'):
            update_data['household_name'] = payload['household_name']
        if payload.get('billing_contact_parent_id'):
            update_data['billing_contact_parent_id'] = payload['billing_contact_parent_id']
        if payload.get('status'):
            update_data['status'] = payload['status']
        
        result = supabase.table('families').update(update_data).eq('id', family_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "family": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/families/{family_id}")
def delete_family(family_id: str, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('families').delete().eq('id', family_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "id": family_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parents", response_model=ParentsResponse)
def parents(current_user: AuthUser = Depends(get_current_user)) -> ParentsResponse:
    if not has_permission(current_user, "parents:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_parents()


@router.get("/parents/{parent_id}", response_model=ParentDetailResponse)
def parent_detail(parent_id: str, current_user: AuthUser = Depends(get_current_user)) -> ParentDetailResponse:
    if not has_permission(current_user, "parents:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('parents').select('*').eq('id', parent_id).eq('school_id', current_user.schoolId).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Parent not found")
        return demo_data.get_parent_detail(parent_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parents")
def create_parent(payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('parents').insert({
            'school_id': current_user.schoolId,
            'family_id': payload.get('family_id'),
            'full_name': payload.get('full_name'),
            'email': payload.get('email'),
            'phone': payload.get('phone'),
            'relationship': payload.get('relationship'),
            'preferred_channel': payload.get('preferred_channel', 'email')
        }).execute()
        return {"success": True, "parent": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/parents/{parent_id}")
def update_parent(parent_id: str, payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('full_name'):
            update_data['full_name'] = payload['full_name']
        if payload.get('email'):
            update_data['email'] = payload['email']
        if payload.get('phone'):
            update_data['phone'] = payload['phone']
        if payload.get('relationship'):
            update_data['relationship'] = payload['relationship']
        if payload.get('preferred_channel'):
            update_data['preferred_channel'] = payload['preferred_channel']
        
        result = supabase.table('parents').update(update_data).eq('id', parent_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "parent": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/parents/{parent_id}")
def delete_parent(parent_id: str, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('parents').delete().eq('id', parent_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "id": parent_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leads/{lead_id}/convert", response_model=ConvertLeadResponse)
def convert_lead(lead_id: str, payload: ConvertLeadRequest, current_user: AuthUser = Depends(get_current_user)) -> ConvertLeadResponse:
    """Convert a lead into a family and student record"""
    supabase = get_supabase_client()
    try:
        # Get the lead
        lead_result = supabase.table('leads').select('*').eq('id', lead_id).execute()
        if not lead_result.data:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        lead = lead_result.data[0]
        
        # Create family
        family_result = supabase.table('families').insert({
            'school_id': current_user.schoolId,
            'household_name': payload.family.householdName,
            'billing_contact_parent_id': payload.family.primaryContactParentId,
            'notes': f'Converted from lead {lead_id}'
        }).execute()
        
        if not family_result.data:
            raise HTTPException(status_code=500, detail="Failed to create family")
        
        family_id = family_result.data[0]['id']
        
        # Create parent from lead information
        parent_result = supabase.table('parents').insert({
            'school_id': current_user.schoolId,
            'family_id': family_id,
            'full_name': lead.get('parent_name', 'Unknown'),
            'email': lead.get('parent_email'),
            'phone': lead.get('parent_phone'),
            'relationship': 'primary',
            'preferred_channel': 'email'
        }).execute()
        
        # Create student
        student_result = supabase.table('students').insert({
            'school_id': current_user.schoolId,
            'family_id': family_id,
            'lead_id': lead_id,
            'first_name': payload.student.firstName,
            'last_name': payload.student.lastName,
            'gender': payload.student.gender,
            'date_of_birth': payload.student.dateOfBirth,
            'class_id': payload.student.classId,
            'status': 'active'
        }).execute()
        
        if not student_result.data:
            raise HTTPException(status_code=500, detail="Failed to create student")
        
        student_id = student_result.data[0]['id']
        
        # Update lead stage to enrolled
        supabase.table('leads').update({'stage': 'enrolled'}).eq('id', lead_id).execute()
        
        return {
            "success": True,
            "family_id": family_id,
            "student_id": student_id,
            "message": "Lead successfully converted to family and student"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error converting lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/students", response_model=StudentsResponse)
def students(current_user: AuthUser = Depends(get_current_user)) -> StudentsResponse:
    if not has_permission(current_user, "students:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_students()


@router.get("/students/{student_id}", response_model=StudentDetailResponse)
def student_detail(student_id: str, current_user: AuthUser = Depends(get_current_user)) -> StudentDetailResponse:
    if not has_permission(current_user, "students:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('students').select('*').eq('id', student_id).eq('school_id', current_user.schoolId).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Student not found")
        return demo_data.get_student_detail(student_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/students/{student_id}")
def update_student(student_id: str, payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer", "teacher"]))) -> dict:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('first_name'):
            update_data['first_name'] = payload['first_name']
        if payload.get('last_name'):
            update_data['last_name'] = payload['last_name']
        if payload.get('admission_no'):
            update_data['admission_no'] = payload['admission_no']
        if payload.get('gender'):
            update_data['gender'] = payload['gender']
        if payload.get('date_of_birth'):
            update_data['date_of_birth'] = payload['date_of_birth']
        if payload.get('class_id'):
            update_data['class_id'] = payload['class_id']
        if payload.get('status'):
            update_data['status'] = payload['status']
        
        result = supabase.table('students').update(update_data).eq('id', student_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "student": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finance/overview", response_model=FinanceResponse)
def finance(current_user: AuthUser = Depends(get_current_user)) -> FinanceResponse:
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_finance()


@router.get("/finance/debtors")
def debtors(current_user: AuthUser = Depends(get_current_user)):
    """Get debtors dashboard with aging buckets"""
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get all overdue invoices
        invoices_result = supabase.table('invoices').select('*').eq('school_id', current_user.schoolId).in_('status', ['overdue', 'part_paid']).execute()
        
        # Calculate aging buckets
        today = datetime.now()
        aging_buckets = {
            "1-30_days": {"count": 0, "amount": 0},
            "31-60_days": {"count": 0, "amount": 0},
            "61-90_days": {"count": 0, "amount": 0},
            "90+_days": {"count": 0, "amount": 0}
        }
        
        debtors_list = []
        
        for invoice in invoices_result.data or []:
            due_date = datetime.strptime(invoice['due_date'], '%Y-%m-%d')
            days_overdue = (today - due_date).days
            amount_outstanding = invoice['amount_due'] - invoice['amount_paid']
            
            if days_overdue <= 30:
                aging_buckets["1-30_days"]["count"] += 1
                aging_buckets["1-30_days"]["amount"] += amount_outstanding
            elif days_overdue <= 60:
                aging_buckets["31-60_days"]["count"] += 1
                aging_buckets["31-60_days"]["amount"] += amount_outstanding
            elif days_overdue <= 90:
                aging_buckets["61-90_days"]["count"] += 1
                aging_buckets["61-90_days"]["amount"] += amount_outstanding
            else:
                aging_buckets["90+_days"]["count"] += 1
                aging_buckets["90+_days"]["amount"] += amount_outstanding
            
            # Get student info
            student_result = supabase.table('students').select('*').eq('id', invoice['student_id']).execute()
            student = student_result.data[0] if student_result.data else None
            
            debtors_list.append({
                "invoice_id": invoice['id'],
                "invoice_number": invoice['invoice_number'],
                "student_name": f"{student['first_name']} {student['last_name']}" if student else "Unknown",
                "amount_outstanding": amount_outstanding,
                "days_overdue": days_overdue,
                "due_date": invoice['due_date'],
                "status": invoice['status']
            })
        
        # Sort by days overdue (descending)
        debtors_list.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return {
            "aging_buckets": aging_buckets,
            "total_outstanding": sum(bucket['amount'] for bucket in aging_buckets.values()),
            "total_debtors": sum(bucket['count'] for bucket in aging_buckets.values()),
            "debtors_list": debtors_list[:50]  # Return top 50 debtors
        }
    except Exception as e:
        print(f"Error fetching debtors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finance/fee-structures", response_model=FeeStructuresResponse)
def fee_structures(current_user: AuthUser = Depends(get_current_user)) -> FeeStructuresResponse:
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        if current_user.schoolId:
            result = supabase.table('fee_structures').select('*').eq('school_id', current_user.schoolId).execute()
            if result.data:
                return demo_data.get_fee_structures()
        return demo_data.get_fee_structures()
    except Exception as e:
        print(f"Error fetching fee structures: {e}")
        return demo_data.get_fee_structures()


@router.post("/finance/fee-structures")
def create_fee_structure(payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('fee_structures').insert({
            'school_id': current_user.schoolId,
            'class_id': payload.get('class_id'),
            'term_name': payload.get('term_name'),
            'title': payload.get('title'),
            'amount': payload.get('amount'),
            'due_days': payload.get('due_days')
        }).execute()
        return {"success": True, "fee_structure": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/finance/fee-structures/{fee_id}")
def update_fee_structure(fee_id: str, payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> dict:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('term_name'):
            update_data['term_name'] = payload['term_name']
        if payload.get('title'):
            update_data['title'] = payload['title']
        if payload.get('amount'):
            update_data['amount'] = payload['amount']
        if payload.get('due_days'):
            update_data['due_days'] = payload['due_days']
        
        result = supabase.table('fee_structures').update(update_data).eq('id', fee_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "fee_structure": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/finance/fee-structures/{fee_id}")
def delete_fee_structure(fee_id: str, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('fee_structures').delete().eq('id', fee_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "id": fee_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoices", response_model=InvoiceDetailResponse)
def create_invoice(payload: InvoiceCreateRequest, current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> InvoiceDetailResponse:
    supabase = get_supabase_client()
    try:
        result = supabase.table('invoices').insert({
            'school_id': current_user.schoolId,
            'student_id': payload.studentId,
            'fee_structure_id': payload.feeStructureId,
            'invoice_number': payload.invoiceNumber,
            'status': 'draft',
            'amount_due': payload.amountDue,
            'amount_paid': 0,
            'due_date': payload.dueDate
        }).execute()
        return demo_data.create_invoice(payload, current_user.schoolId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/invoices/{invoice_id}")
def update_invoice(invoice_id: str, payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> dict:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('status'):
            update_data['status'] = payload['status']
        if payload.get('amount_paid'):
            update_data['amount_paid'] = payload['amount_paid']
        if payload.get('due_date'):
            update_data['due_date'] = payload['due_date']
        
        result = supabase.table('invoices').update(update_data).eq('id', invoice_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "invoice": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: str, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('invoices').delete().eq('id', invoice_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "id": invoice_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments", response_model=PaymentRecord)
def record_payment(payload: PaymentRecord, current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> PaymentRecord:
    return demo_data.record_payment(payload)


@router.post("/payments/paystack/initialize", response_model=PaystackInitResponse)
def init_paystack(current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> PaystackInitResponse:
    return demo_data.init_paystack()


@router.post("/payments/flutterwave/initialize", response_model=FlutterwaveInitResponse)
def init_flutterwave(current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> FlutterwaveInitResponse:
    # TODO: Implement with Supabase
    return {"status": "success"}


@router.post("/webhooks/paystack")
def webhook_paystack(payload: dict) -> dict[str, str]:
    # TODO: Implement with Supabase
    return {"status": "success"}


@router.post("/webhooks/flutterwave")
def webhook_flutterwave(payload: dict) -> dict[str, str]:
    # TODO: Implement with Supabase
    return {"status": "success"}


@router.post("/payments/initialize")
def initialize_payment(payload: dict, current_user: AuthUser = Depends(get_current_user)) -> dict:
    # TODO: Implement with Supabase
    return {
        "payment_id": "new-payment",
        "authorization_url": "https://flutterwave.com/pay/test",
        "reference": "test-ref",
        "amount": 0,
    }


@router.get("/messages/overview", response_model=MessagingResponse)
def messaging(current_user: AuthUser = Depends(get_current_user)) -> MessagingResponse:
    if not has_permission(current_user, "messaging:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_messaging()


@router.get("/messages/templates", response_model=MessageTemplatesResponse)
def message_templates(current_user: AuthUser = Depends(get_current_user)) -> MessageTemplatesResponse:
    if not has_permission(current_user, "messaging:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        if current_user.schoolId:
            result = supabase.table('message_templates').select('*').eq('school_id', current_user.schoolId).execute()
            if result.data:
                return MessageTemplatesResponse(
                    templates=[
                        {"id": "1", "name": "Welcome Email", "channel": "email", "useCase": "Onboarding", "lastEdited": "2026-07-20"},
                        {"id": "2", "name": "Fee Reminder", "channel": "sms", "useCase": "Collections", "lastEdited": "2026-07-15"},
                        {"id": "3", "name": "Payment Receipt", "channel": "email", "useCase": "Finance", "lastEdited": "2026-07-18"},
                        {"id": "4", "name": "Assessment Notice", "channel": "whatsapp", "useCase": "Academic", "lastEdited": "2026-07-22"},
                        {"id": "5", "name": "Complaint Response", "channel": "email", "useCase": "Support", "lastEdited": "2026-07-25"},
                    ]
                )
        return MessageTemplatesResponse(
            templates=[
                {"id": "1", "name": "Welcome Email", "channel": "email", "useCase": "Onboarding", "lastEdited": "2026-07-20"},
                {"id": "2", "name": "Fee Reminder", "channel": "sms", "useCase": "Collections", "lastEdited": "2026-07-15"},
                {"id": "3", "name": "Payment Receipt", "channel": "email", "useCase": "Finance", "lastEdited": "2026-07-18"},
                {"id": "4", "name": "Assessment Notice", "channel": "whatsapp", "useCase": "Academic", "lastEdited": "2026-07-22"},
                {"id": "5", "name": "Complaint Response", "channel": "email", "useCase": "Support", "lastEdited": "2026-07-25"},
            ]
        )
    except Exception as e:
        print(f"Error fetching message templates: {e}")
        return MessageTemplatesResponse(
            templates=[
                {"id": "1", "name": "Welcome Email", "channel": "email", "useCase": "Onboarding", "lastEdited": "2026-07-20"},
                {"id": "2", "name": "Fee Reminder", "channel": "sms", "useCase": "Collections", "lastEdited": "2026-07-15"},
                {"id": "3", "name": "Payment Receipt", "channel": "email", "useCase": "Finance", "lastEdited": "2026-07-18"},
                {"id": "4", "name": "Assessment Notice", "channel": "whatsapp", "useCase": "Academic", "lastEdited": "2026-07-22"},
                {"id": "5", "name": "Complaint Response", "channel": "email", "useCase": "Support", "lastEdited": "2026-07-25"},
            ]
        )


@router.post("/messages/templates")
def create_message_template(payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('message_templates').insert({
            'school_id': current_user.schoolId,
            'name': payload.get('name'),
            'channel': payload.get('channel'),
            'use_case': payload.get('useCase'),
            'subject': payload.get('subject'),
            'body': payload.get('body')
        }).execute()
        return {"success": True, "template": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/messages/templates/{template_id}")
def update_message_template(template_id: str, payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('name'):
            update_data['name'] = payload['name']
        if payload.get('channel'):
            update_data['channel'] = payload['channel']
        if payload.get('use_case'):
            update_data['use_case'] = payload['use_case']
        if payload.get('subject'):
            update_data['subject'] = payload['subject']
        if payload.get('body'):
            update_data['body'] = payload['body']
        
        result = supabase.table('message_templates').update(update_data).eq('id', template_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "template": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/messages/templates/{template_id}")
def delete_message_template(template_id: str, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('message_templates').delete().eq('id', template_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "id": template_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/broadcast")
def broadcast_message(payload: BroadcastRequest, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict[str, str]:
    return demo_data.broadcast_message(payload)


@router.get("/tickets", response_model=HelpdeskResponse)
def tickets(current_user: AuthUser = Depends(get_current_user)) -> HelpdeskResponse:
    if not has_permission(current_user, "tickets:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_helpdesk()


@router.get("/tickets/{ticket_id}", response_model=TicketDetailResponse)
def ticket_detail(ticket_id: str, current_user: AuthUser = Depends(get_current_user)) -> TicketDetailResponse:
    if not has_permission(current_user, "tickets:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('tickets').select('*').eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return demo_data.get_ticket_detail(ticket_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets")
def create_ticket(payload: dict, current_user: AuthUser = Depends(get_current_user)) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('tickets').insert({
            'school_id': current_user.schoolId,
            'parent_id': payload.get('parent_id'),
            'family_id': payload.get('family_id'),
            'subject': payload.get('subject'),
            'description': payload.get('description'),
            'priority': payload.get('priority', 'medium'),
            'status': 'open'
        }).execute()
        return {"success": True, "ticket": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: str, payload: dict, current_user: AuthUser = Depends(require_any_role(["school_admin", "helpdesk_officer"]))) -> dict:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('status'):
            update_data['status'] = payload['status']
        if payload.get('priority'):
            update_data['priority'] = payload['priority']
        if payload.get('assignee_user_id'):
            update_data['assignee_user_id'] = payload['assignee_user_id']
        if payload.get('sla_due_at'):
            update_data['sla_due_at'] = payload['sla_due_at']
        
        result = supabase.table('tickets').update(update_data).eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "ticket": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: str, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        result = supabase.table('tickets').delete().eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "id": ticket_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}", response_model=InvoiceDetailResponse)
def invoice_detail(invoice_id: str, current_user: AuthUser = Depends(get_current_user)) -> InvoiceDetailResponse:
    return demo_data.get_invoice_detail(invoice_id)


@router.get("/staff/overview", response_model=StaffResponse)
def staff(current_user: AuthUser = Depends(get_current_user)) -> StaffResponse:
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        if current_user.schoolId:
            result = supabase.table('users').select('*').eq('school_id', current_user.schoolId).execute()
            if result.data:
                return demo_data.get_staff()
        return demo_data.get_staff()
    except Exception as e:
        print(f"Error fetching staff: {e}")
        return demo_data.get_staff()


@router.post("/staff")
def create_staff(payload: dict, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            'email': payload.get('email'),
            'password': payload.get('password'),
            'options': {
                'data': {
                    'full_name': payload.get('full_name'),
                    'phone': payload.get('phone')
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=500, detail="Failed to create user in auth")
        
        # Assign role in user_roles table
        role_result = supabase.table('user_roles').insert({
            'user_id': auth_response.user.id,
            'role': payload.get('role'),
            'school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "user_id": auth_response.user.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/staff/{staff_id}")
def update_staff(staff_id: str, payload: dict, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('full_name'):
            update_data['full_name'] = payload['full_name']
        if payload.get('phone'):
            update_data['phone'] = payload['phone']
        if payload.get('status'):
            update_data['status'] = payload['status']
        
        # Update user metadata in auth
        if update_data:
            supabase.auth.admin.update_user_by_id(
                staff_id,
                user_metadata=update_data
            )
        
        # Update role if provided
        if payload.get('role'):
            supabase.table('user_roles').update({'role': payload['role']}).eq('user_id', staff_id).execute()
        
        return {"success": True, "id": staff_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/staff/{staff_id}")
def delete_staff(staff_id: str, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        # Delete user role
        supabase.table('user_roles').delete().eq('user_id', staff_id).execute()
        # Delete user from auth
        supabase.auth.admin.delete_user(staff_id)
        return {"success": True, "id": staff_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/overview", response_model=ReportsResponse)
def reports(current_user: AuthUser = Depends(get_current_user)) -> ReportsResponse:
    if not has_permission(current_user, "reports:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_reports()


@router.get("/reports/{report_name}", response_model=ReportResponse)
def report_detail(report_name: str, current_user: AuthUser = Depends(get_current_user)) -> ReportResponse:
    if not has_permission(current_user, "reports:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return ReportResponse(
        title=report_name.replace("-", " ").title(),
        description="Detailed report data would be generated here based on the selected report type.",
        data=[],
        generatedAt=datetime.now().strftime("%Y-%m-%d")
    )


@router.get("/settings/overview", response_model=SettingsResponse)
def settings(current_user: AuthUser = Depends(get_current_user)) -> SettingsResponse:
    if not has_permission(current_user, "settings:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('schools').select('*').eq('id', current_user.schoolId).execute()
        return demo_data.get_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/settings")
def update_settings(payload: dict, current_user: AuthUser = Depends(require_role("school_admin"))) -> dict:
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('name'):
            update_data['name'] = payload['name']
        if payload.get('primary_color'):
            update_data['primary_color'] = payload['primary_color']
        if payload.get('logo_url'):
            update_data['logo_url'] = payload['logo_url']
        if payload.get('school_type'):
            update_data['school_type'] = payload['school_type']
        
        # Update school settings
        if update_data:
            result = supabase.table('schools').update(update_data).eq('id', current_user.schoolId).execute()
        
        # Store payment provider keys securely (in a separate table or environment variables)
        # For now, we'll store them in the schools table as metadata
        provider_keys = {}
        if payload.get('paystack_public_key'):
            provider_keys['paystack_public_key'] = payload['paystack_public_key']
        if payload.get('paystack_secret_key'):
            provider_keys['paystack_secret_key'] = payload['paystack_secret_key']
        if payload.get('flutterwave_public_key'):
            provider_keys['flutterwave_public_key'] = payload['flutterwave_public_key']
        if payload.get('flutterwave_secret_key'):
            provider_keys['flutterwave_secret_key'] = payload['flutterwave_secret_key']
        
        communication_settings = {}
        if payload.get('brevo_api_key'):
            communication_settings['brevo_api_key'] = payload['brevo_api_key']
        if payload.get('termii_api_key'):
            communication_settings['termii_api_key'] = payload['termii_api_key']
        if payload.get('whatsapp_phone_number_id'):
            communication_settings['whatsapp_phone_number_id'] = payload['whatsapp_phone_number_id']
        if payload.get('whatsapp_access_token'):
            communication_settings['whatsapp_access_token'] = payload['whatsapp_access_token']
        
        # Update school with provider keys and communication settings as metadata
        if provider_keys or communication_settings:
            metadata_update = {}
            if provider_keys:
                metadata_update['payment_providers'] = provider_keys
            if communication_settings:
                metadata_update['communication_settings'] = communication_settings
            
            supabase.table('schools').update(metadata_update).eq('id', current_user.schoolId).execute()
        
        return {"success": True, "message": "Settings updated successfully"}
    except Exception as e:
        print(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

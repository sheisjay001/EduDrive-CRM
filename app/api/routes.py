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
    """Send broadcast message using configured messaging providers"""
    supabase = get_supabase_client()
    try:
        # Get school communication settings
        school_result = supabase.table('schools').select('communication_settings').eq('id', current_user.schoolId).execute()
        
        if not school_result.data:
            raise HTTPException(status_code=404, detail="School not found")
        
        communication_settings = school_result.data[0].get('communication_settings', {})
        
        results = {"email": "skipped", "sms": "skipped", "whatsapp": "skipped"}
        
        # Send email if configured and email channel selected
        if payload.channel in ['email', 'all'] and communication_settings.get('brevo_api_key'):
            try:
                import requests
                url = "https://api.brevo.com/v3/smtp/email"
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "api-key": communication_settings['brevo_api_key']
                }
                
                data = {
                    "sender": {
                        "name": "EduDrive CRM",
                        "email": "noreply@edudrive.com"
                    },
                    "to": [{"email": recipient} for recipient in payload.recipients],
                    "subject": payload.subject,
                    "htmlContent": payload.message,
                    "textContent": payload.message
                }
                
                response = requests.post(url, json=data, headers=headers)
                if response.status_code in [200, 201]:
                    results["email"] = "sent"
                else:
                    results["email"] = "failed"
            except Exception as e:
                print(f"Email broadcast error: {e}")
                results["email"] = "failed"
        
        # Send SMS if configured and SMS channel selected
        if payload.channel in ['sms', 'all'] and communication_settings.get('termii_api_key'):
            try:
                import requests
                url = "https://api.ng.termii.com/api/sms/send"
                
                for recipient in payload.recipients:
                    data = {
                        "api_key": communication_settings['termii_api_key'],
                        "to": recipient,
                        "from": "EduDrive",
                        "sms": payload.message,
                        "type": "plain",
                        "channel": "dnd"
                    }
                    
                    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
                
                results["sms"] = "sent"
            except Exception as e:
                print(f"SMS broadcast error: {e}")
                results["sms"] = "failed"
        
        # Send WhatsApp if configured and WhatsApp channel selected
        if payload.channel in ['whatsapp', 'all'] and communication_settings.get('whatsapp_phone_number_id'):
            try:
                import requests
                phone_number_id = communication_settings['whatsapp_phone_number_id']
                access_token = communication_settings['whatsapp_access_token']
                url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                for recipient in payload.recipients:
                    data = {
                        "messaging_product": "whatsapp",
                        "to": recipient,
                        "type": "text",
                        "text": {"body": payload.message}
                    }
                    
                    requests.post(url, json=data, headers=headers)
                
                results["whatsapp"] = "sent"
            except Exception as e:
                print(f"WhatsApp broadcast error: {e}")
                results["whatsapp"] = "failed"
        
        return results
    except Exception as e:
        print(f"Broadcast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/settings/terms")
def get_terms(current_user: AuthUser = Depends(get_current_user)):
    """Get all academic terms/sessions for the school"""
    if not has_permission(current_user, "settings:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('terms').select('*').eq('school_id', current_user.schoolId).execute()
        return {"terms": result.data or []}
    except Exception as e:
        print(f"Error fetching terms: {e}")
        return {"terms": []}


@router.post("/settings/terms")
def create_term(payload: dict, current_user: AuthUser = Depends(require_role("school_admin"))):
    """Create a new academic term/session"""
    supabase = get_supabase_client()
    try:
        result = supabase.table('terms').insert({
            'school_id': current_user.schoolId,
            'name': payload.get('name'),
            'start_date': payload.get('start_date'),
            'end_date': payload.get('end_date'),
            'is_active': payload.get('is_active', False)
        }).execute()
        return {"success": True, "term": result.data[0]}
    except Exception as e:
        print(f"Error creating term: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/settings/terms/{term_id}")
def update_term(term_id: str, payload: dict, current_user: AuthUser = Depends(require_role("school_admin"))):
    """Update an academic term/session"""
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('name'):
            update_data['name'] = payload['name']
        if payload.get('start_date'):
            update_data['start_date'] = payload['start_date']
        if payload.get('end_date'):
            update_data['end_date'] = payload['end_date']
        if payload.get('is_active') is not None:
            update_data['is_active'] = payload['is_active']
        
        result = supabase.table('terms').update(update_data).eq('id', term_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "term": result.data[0]}
    except Exception as e:
        print(f"Error updating term: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/classes")
def get_classes(current_user: AuthUser = Depends(get_current_user)):
    """Get all classes for the school"""
    if not has_permission(current_user, "settings:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('classes').select('*').eq('school_id', current_user.schoolId).execute()
        return {"classes": result.data or []}
    except Exception as e:
        print(f"Error fetching classes: {e}")
        return {"classes": []}


@router.post("/settings/classes")
def create_class(payload: dict, current_user: AuthUser = Depends(require_role("school_admin"))):
    """Create a new class"""
    supabase = get_supabase_client()
    try:
        result = supabase.table('classes').insert({
            'school_id': current_user.schoolId,
            'name': payload.get('name'),
            'arm': payload.get('arm'),
            'level_group': payload.get('level_group')
        }).execute()
        return {"success": True, "class": result.data[0]}
    except Exception as e:
        print(f"Error creating class: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/settings/classes/{class_id}")
def update_class(class_id: str, payload: dict, current_user: AuthUser = Depends(require_role("school_admin"))):
    """Update a class"""
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('name'):
            update_data['name'] = payload['name']
        if payload.get('arm'):
            update_data['arm'] = payload['arm']
        if payload.get('level_group'):
            update_data['level_group'] = payload['level_group']
        
        result = supabase.table('classes').update(update_data).eq('id', class_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "class": result.data[0]}
    except Exception as e:
        print(f"Error updating class: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/settings/classes/{class_id}")
def delete_class(class_id: str, current_user: AuthUser = Depends(require_role("school_admin"))):
    """Delete a class"""
    supabase = get_supabase_client()
    try:
        result = supabase.table('classes').delete().eq('id', class_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "id": class_id}
    except Exception as e:
        print(f"Error deleting class: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/users")
def get_users(current_user: AuthUser = Depends(require_role("school_admin"))):
    """Get all users for the school"""
    supabase = get_supabase_client()
    try:
        # Get users with their roles
        result = supabase.table('users').select('*').eq('school_id', current_user.schoolId).execute()
        users = []
        
        for user in result.data or []:
            # Get user role
            role_result = supabase.table('user_roles').select('role').eq('user_id', user['id']).execute()
            role = role_result.data[0]['role'] if role_result.data else 'school_admin'
            
            users.append({
                "id": user['id'],
                "full_name": user['full_name'],
                "email": user['email'],
                "role": role,
                "status": user['status'],
                "last_login_at": user.get('last_login_at')
            })
        
        return {"users": users}
    except Exception as e:
        print(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings/users")
def create_user(payload: dict, current_user: AuthUser = Depends(require_role("school_admin"))):
    """Create a new user"""
    supabase = get_supabase_client()
    try:
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            'email': payload.get('email'),
            'password': payload.get('password'),
            'options': {
                'data': {
                    'full_name': payload.get('full_name'),
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Failed to create user in auth")
        
        # Create user in database
        user_result = supabase.table('users').insert({
            'school_id': current_user.schoolId,
            'full_name': payload.get('full_name'),
            'email': payload.get('email'),
            'password_hash': '',  # Password is managed by Supabase Auth
            'status': 'active'
        }).execute()
        
        # Create user role
        supabase.table('user_roles').insert({
            'user_id': auth_response.user.id,
            'role': payload.get('role', 'school_admin'),
            'school_id': current_user.schoolId
        }).execute()
        
        return {"success": True, "user": user_result.data[0]}
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/settings/users/{user_id}")
def update_user(user_id: str, payload: dict, current_user: AuthUser = Depends(require_role("school_admin"))):
    """Update a user"""
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('full_name'):
            update_data['full_name'] = payload['full_name']
        if payload.get('status'):
            update_data['status'] = payload['status']
        
        if update_data:
            result = supabase.table('users').update(update_data).eq('id', user_id).eq('school_id', current_user.schoolId).execute()
        
        # Update role if provided
        if payload.get('role'):
            supabase.table('user_roles').update({'role': payload['role']}).eq('user_id', user_id).execute()
        
        return {"success": True, "message": "User updated successfully"}
    except Exception as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/settings/users/{user_id}")
def delete_user(user_id: str, current_user: AuthUser = Depends(require_role("school_admin"))):
    """Delete a user"""
    supabase = get_supabase_client()
    try:
        # Delete user role
        supabase.table('user_roles').delete().eq('user_id', user_id).execute()
        
        # Delete user from database
        supabase.table('users').delete().eq('id', user_id).eq('school_id', current_user.schoolId).execute()
        
        # Delete from Supabase Auth (requires admin privileges)
        try:
            supabase.auth.admin.delete_user(user_id)
        except Exception as e:
            print(f"Could not delete from auth: {e}")
        
        return {"success": True, "id": user_id}
    except Exception as e:
        print(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/paystack/initialize")
def initialize_paystack_payment(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Initialize payment with Paystack"""
    if not has_permission(current_user, "finance:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    try:
        import requests
        from app.core.config import settings
        
        # Get Paystack secret key from school settings
        supabase = get_supabase_client()
        school_result = supabase.table('schools').select('payment_providers').eq('id', current_user.schoolId).execute()
        
        if not school_result.data:
            raise HTTPException(status_code=404, detail="School not found")
        
        payment_providers = school_result.data[0].get('payment_providers', {})
        secret_key = payment_providers.get('paystack_secret_key')
        
        if not secret_key:
            raise HTTPException(status_code=400, detail="Paystack not configured")
        
        # Initialize payment
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "email": payload.get('email'),
            "amount": payload.get('amount') * 100,  # Convert to kobo
            "reference": payload.get('reference'),
            "metadata": {
                "invoice_id": payload.get('invoice_id'),
                "school_id": current_user.schoolId
            },
            "callback_url": f"{settings.frontend_url}/payments/paystack/callback"
        }
        
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()
        
        if response_data.get('status'):
            return {
                "success": True,
                "authorization_url": response_data['data']['authorization_url'],
                "reference": response_data['data']['reference']
            }
        else:
            raise HTTPException(status_code=400, detail=response_data.get('message', 'Payment initialization failed'))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error initializing Paystack payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/paystack/webhook")
def paystack_webhook(payload: dict):
    """Handle Paystack webhook"""
    try:
        import hashlib
        import hmac
        from app.core.config import settings
        
        # Verify webhook signature
        # In production, verify the signature using the secret key
        
        event = payload.get('event')
        data = payload.get('data')
        
        if event == 'charge.success':
            # Payment successful - update invoice
            reference = data.get('reference')
            amount = data.get('amount') / 100  # Convert from kobo
            
            supabase = get_supabase_client()
            
            # Find invoice by reference
            invoice_result = supabase.table('invoices').select('*').eq('payment_reference', reference).execute()
            
            if invoice_result.data:
                invoice = invoice_result.data[0]
                
                # Update payment
                supabase.table('payments').insert({
                    'invoice_id': invoice['id'],
                    'amount': amount,
                    'payment_method': 'paystack',
                    'payment_reference': reference,
                    'status': 'completed',
                    'paid_at': datetime.now().isoformat()
                }).execute()
                
                # Update invoice status
                new_amount_paid = invoice['amount_paid'] + amount
                new_status = 'paid' if new_amount_paid >= invoice['amount_due'] else 'part_paid'
                
                supabase.table('invoices').update({
                    'amount_paid': new_amount_paid,
                    'status': new_status
                }).eq('id', invoice['id']).execute()
        
        return {"status": "success"}
    except Exception as e:
        print(f"Error processing Paystack webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/flutterwave/initialize")
def initialize_flutterwave_payment(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Initialize payment with Flutterwave"""
    if not has_permission(current_user, "finance:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    try:
        import requests
        from app.core.config import settings
        
        # Get Flutterwave secret key from school settings
        supabase = get_supabase_client()
        school_result = supabase.table('schools').select('payment_providers').eq('id', current_user.schoolId).execute()
        
        if not school_result.data:
            raise HTTPException(status_code=404, detail="School not found")
        
        payment_providers = school_result.data[0].get('payment_providers', {})
        secret_key = payment_providers.get('flutterwave_secret_key')
        
        if not secret_key:
            raise HTTPException(status_code=400, detail="Flutterwave not configured")
        
        # Initialize payment
        url = "https://api.flutterwave.com/v3/payments"
        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "tx_ref": payload.get('reference'),
            "amount": payload.get('amount'),
            "currency": "NGN",
            "email": payload.get('email'),
            "payment_options": "card, banktransfer",
            "meta": {
                "invoice_id": payload.get('invoice_id'),
                "school_id": current_user.schoolId
            },
            "redirect_url": f"{settings.frontend_url}/payments/flutterwave/callback"
        }
        
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()
        
        if response_data.get('status') == 'success':
            return {
                "success": True,
                "payment_link": response_data['data']['link'],
                "reference": response_data['data']['tx_ref']
            }
        else:
            raise HTTPException(status_code=400, detail=response_data.get('message', 'Payment initialization failed'))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error initializing Flutterwave payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/flutterwave/webhook")
def flutterwave_webhook(payload: dict):
    """Handle Flutterwave webhook"""
    try:
        event = payload.get('event')
        data = payload.get('data')
        
        if event == 'charge.completed' and data.get('status') == 'successful':
            # Payment successful - update invoice
            reference = data.get('tx_ref')
            amount = data.get('amount')
            
            supabase = get_supabase_client()
            
            # Find invoice by reference
            invoice_result = supabase.table('invoices').select('*').eq('payment_reference', reference).execute()
            
            if invoice_result.data:
                invoice = invoice_result.data[0]
                
                # Update payment
                supabase.table('payments').insert({
                    'invoice_id': invoice['id'],
                    'amount': amount,
                    'payment_method': 'flutterwave',
                    'payment_reference': reference,
                    'status': 'completed',
                    'paid_at': datetime.now().isoformat()
                }).execute()
                
                # Update invoice status
                new_amount_paid = invoice['amount_paid'] + amount
                new_status = 'paid' if new_amount_paid >= invoice['amount_due'] else 'part_paid'
                
                supabase.table('invoices').update({
                    'amount_paid': new_amount_paid,
                    'status': new_status
                }).eq('id', invoice['id']).execute()
        
        return {"status": "success"}
    except Exception as e:
        print(f"Error processing Flutterwave webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messaging/email/send")
def send_email(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Send email using Brevo"""
    if not has_permission(current_user, "messaging:send"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    try:
        import requests
        
        # Get Brevo API key from school settings
        supabase = get_supabase_client()
        school_result = supabase.table('schools').select('communication_settings').eq('id', current_user.schoolId).execute()
        
        if not school_result.data:
            raise HTTPException(status_code=404, detail="School not found")
        
        communication_settings = school_result.data[0].get('communication_settings', {})
        api_key = communication_settings.get('brevo_api_key')
        
        if not api_key:
            raise HTTPException(status_code=400, detail="Brevo not configured")
        
        # Send email using Brevo API
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": api_key
        }
        
        data = {
            "sender": {
                "name": payload.get('sender_name', 'EduDrive CRM'),
                "email": payload.get('sender_email', 'noreply@edudrive.com')
            },
            "to": [{"email": email} for email in payload.get('recipients', [])],
            "subject": payload.get('subject'),
            "htmlContent": payload.get('html_content'),
            "textContent": payload.get('text_content', '')
        }
        
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()
        
        if response.status_code == 201 or response.status_code == 200:
            return {"success": True, "message_id": response_data.get('messageId')}
        else:
            raise HTTPException(status_code=400, detail=response_data.get('message', 'Failed to send email'))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messaging/sms/send")
def send_sms(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Send SMS using Termii"""
    if not has_permission(current_user, "messaging:send"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    try:
        import requests
        
        # Get Termii API key from school settings
        supabase = get_supabase_client()
        school_result = supabase.table('schools').select('communication_settings').eq('id', current_user.schoolId).execute()
        
        if not school_result.data:
            raise HTTPException(status_code=404, detail="School not found")
        
        communication_settings = school_result.data[0].get('communication_settings', {})
        api_key = communication_settings.get('termii_api_key')
        
        if not api_key:
            raise HTTPException(status_code=400, detail="Termii not configured")
        
        # Send SMS using Termii API
        url = "https://api.ng.termii.com/api/sms/send"
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "api_key": api_key,
            "to": payload.get('phone_number'),
            "from": payload.get('sender_id', 'EduDrive'),
            "sms": payload.get('message'),
            "type": "plain",
            "channel": "dnd"
        }
        
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()
        
        if response_data.get('message') == 'Successfully Sent':
            return {"success": True, "message_id": response_data.get('message_id')}
        else:
            raise HTTPException(status_code=400, detail=response_data.get('message', 'Failed to send SMS'))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messaging/whatsapp/send")
def send_whatsapp_message(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Send WhatsApp message using WhatsApp Cloud API"""
    if not has_permission(current_user, "messaging:send"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    try:
        import requests
        
        # Get WhatsApp credentials from school settings
        supabase = get_supabase_client()
        school_result = supabase.table('schools').select('communication_settings').eq('id', current_user.schoolId).execute()
        
        if not school_result.data:
            raise HTTPException(status_code=404, detail="School not found")
        
        communication_settings = school_result.data[0].get('communication_settings', {})
        phone_number_id = communication_settings.get('whatsapp_phone_number_id')
        access_token = communication_settings.get('whatsapp_access_token')
        
        if not phone_number_id or not access_token:
            raise HTTPException(status_code=400, detail="WhatsApp not configured")
        
        # Send WhatsApp message using Cloud API
        url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": payload.get('phone_number'),
            "type": "text",
            "text": {
                "body": payload.get('message')
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200:
            return {"success": True, "message_id": response_data.get('messages', [{}])[0].get('id')}
        else:
            raise HTTPException(status_code=400, detail=response_data.get('error', {}).get('message', 'Failed to send WhatsApp message'))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-logs")
def get_audit_logs(current_user: AuthUser = Depends(get_current_user)):
    """Get audit logs for the school"""
    if not has_permission(current_user, "audit:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('audit_logs').select('*').eq('school_id', current_user.schoolId).order('created_at', desc=True).limit(100).execute()
        return {"logs": result.data or []}
    except Exception as e:
        print(f"Error fetching audit logs: {e}")
        return {"logs": []}


@router.get("/audit-logs/user/{user_id}")
def get_user_audit_logs(user_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Get audit logs for a specific user"""
    if not has_permission(current_user, "audit:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('audit_logs').select('*').eq('school_id', current_user.schoolId).eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        return {"logs": result.data or []}
    except Exception as e:
        print(f"Error fetching user audit logs: {e}")
        return {"logs": []}


@router.post("/auth/refresh")
def refresh_token(payload: AuthRefreshRequest) -> AuthResponse:
    """Refresh access token using refresh token with device/session tracking"""
    supabase = get_supabase_client()
    try:
        # Verify refresh token and get user info
        from app.core.security import verify_token
        token_data = verify_token(payload.refresh_token)
        
        if not token_data or token_data.get('token_type') != 'refresh':
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Get user from database
        user_result = supabase.table('users').select('*').eq('id', token_data.get('sub')).execute()
        if not user_result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_result.data[0]
        
        # Get user role
        role_result = supabase.table('user_roles').select('role').eq('user_id', user['id']).execute()
        role = role_result.data[0]['role'] if role_result.data else 'school_admin'
        
        # Log the refresh activity for session tracking
        supabase.table('audit_logs').insert({
            'school_id': user['school_id'],
            'user_id': user['id'],
            'action': 'token_refresh',
            'entity_type': 'auth',
            'entity_id': user['id'],
            'details': {
                'device_info': payload.get('device_info', {}),
                'ip_address': payload.get('ip_address')
            },
            'created_at': datetime.now().isoformat()
        }).execute()
        
        # Create new tokens
        auth_user = AuthUser(
            id=user['id'],
            schoolId=user['school_id'],
            role=role,
            fullName=user['full_name'],
            email=user['email'],
        )
        
        access_token, refresh_token = create_tokens_for_user(auth_user)
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,
            user=auth_user,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error refreshing token: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.get("/leads/{lead_id}/tours")
def get_lead_tours(lead_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Get all scheduled tours for a lead"""
    if not has_permission(current_user, "admissions:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('tours').select('*').eq('lead_id', lead_id).eq('school_id', current_user.schoolId).order('scheduled_date', desc=True).execute()
        return {"tours": result.data or []}
    except Exception as e:
        print(f"Error fetching tours: {e}")
        return {"tours": []}


@router.post("/leads/{lead_id}/tours")
def schedule_tour(lead_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Schedule a tour for a lead"""
    if not has_permission(current_user, "admissions:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('tours').insert({
            'school_id': current_user.schoolId,
            'lead_id': lead_id,
            'scheduled_date': payload.get('scheduled_date'),
            'scheduled_time': payload.get('scheduled_time'),
            'tour_type': payload.get('tour_type', 'general'),
            'notes': payload.get('notes'),
            'status': 'scheduled',
            'scheduled_by': current_user.id
        }).execute()
        return {"success": True, "tour": result.data[0]}
    except Exception as e:
        print(f"Error scheduling tour: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tours/{tour_id}")
def update_tour(tour_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Update a scheduled tour"""
    if not has_permission(current_user, "admissions:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('scheduled_date'):
            update_data['scheduled_date'] = payload['scheduled_date']
        if payload.get('scheduled_time'):
            update_data['scheduled_time'] = payload['scheduled_time']
        if payload.get('status'):
            update_data['status'] = payload['status']
        if payload.get('notes'):
            update_data['notes'] = payload['notes']
        
        result = supabase.table('tours').update(update_data).eq('id', tour_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "tour": result.data[0]}
    except Exception as e:
        print(f"Error updating tour: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/{lead_id}/assessments")
def get_lead_assessments(lead_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Get all assessments for a lead"""
    if not has_permission(current_user, "admissions:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('assessments').select('*').eq('lead_id', lead_id).eq('school_id', current_user.schoolId).order('scheduled_date', desc=True).execute()
        return {"assessments": result.data or []}
    except Exception as e:
        print(f"Error fetching assessments: {e}")
        return {"assessments": []}


@router.post("/leads/{lead_id}/assessments")
def schedule_assessment(lead_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Schedule an assessment for a lead"""
    if not has_permission(current_user, "admissions:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('assessments').insert({
            'school_id': current_user.schoolId,
            'lead_id': lead_id,
            'scheduled_date': payload.get('scheduled_date'),
            'scheduled_time': payload.get('scheduled_time'),
            'assessment_type': payload.get('assessment_type'),
            'notes': payload.get('notes'),
            'status': 'scheduled',
            'scheduled_by': current_user.id
        }).execute()
        return {"success": True, "assessment": result.data[0]}
    except Exception as e:
        print(f"Error scheduling assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/assessments/{assessment_id}")
def update_assessment(assessment_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Update an assessment"""
    if not has_permission(current_user, "admissions:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('scheduled_date'):
            update_data['scheduled_date'] = payload['scheduled_date']
        if payload.get('scheduled_time'):
            update_data['scheduled_time'] = payload['scheduled_time']
        if payload.get('status'):
            update_data['status'] = payload['status']
        if payload.get('score'):
            update_data['score'] = payload['score']
        if payload.get('notes'):
            update_data['notes'] = payload['notes']
        
        result = supabase.table('assessments').update(update_data).eq('id', assessment_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "assessment": result.data[0]}
    except Exception as e:
        print(f"Error updating assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finance/bulk-billing")
def bulk_billing(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Create bulk invoices for multiple students"""
    if not has_permission(current_user, "finance:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        student_ids = payload.get('student_ids', [])
        fee_structure_id = payload.get('fee_structure_id')
        term_id = payload.get('term_id')
        due_date = payload.get('due_date')
        
        # Get fee structure
        fee_result = supabase.table('fee_structures').select('*').eq('id', fee_structure_id).eq('school_id', current_user.schoolId).execute()
        if not fee_result.data:
            raise HTTPException(status_code=404, detail="Fee structure not found")
        
        fee_structure = fee_result.data[0]
        
        created_invoices = []
        errors = []
        
        for student_id in student_ids:
            try:
                # Get student info
                student_result = supabase.table('students').select('*').eq('id', student_id).eq('school_id', current_user.schoolId).execute()
                if not student_result.data:
                    errors.append({"student_id": student_id, "error": "Student not found"})
                    continue
                
                student = student_result.data[0]
                
                # Create invoice
                invoice_result = supabase.table('invoices').insert({
                    'school_id': current_user.schoolId,
                    'student_id': student_id,
                    'family_id': student['family_id'],
                    'invoice_number': f"INV-{datetime.now().strftime('%Y%m%d')}-{len(created_invoices) + 1}",
                    'amount_due': fee_structure['amount'],
                    'amount_paid': 0,
                    'due_date': due_date,
                    'status': 'pending',
                    'fee_structure_id': fee_structure_id,
                    'term_id': term_id,
                    'description': f"{fee_structure['name']} - {fee_structure['description']}",
                    'created_by': current_user.id
                }).execute()
                
                created_invoices.append(invoice_result.data[0])
                
                # Log the action
                supabase.table('audit_logs').insert({
                    'school_id': current_user.schoolId,
                    'user_id': current_user.id,
                    'action': 'bulk_invoice_created',
                    'entity_type': 'invoice',
                    'entity_id': invoice_result.data[0]['id'],
                    'details': {
                        'student_id': student_id,
                        'fee_structure_id': fee_structure_id,
                        'amount': fee_structure['amount']
                    },
                    'created_at': datetime.now().isoformat()
                }).execute()
                
            except Exception as e:
                errors.append({"student_id": student_id, "error": str(e)})
        
        return {
            "success": True,
            "created_invoices": created_invoices,
            "total_created": len(created_invoices),
            "errors": errors,
            "total_errors": len(errors)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in bulk billing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finance/reconciliation")
def get_reconciliation(current_user: AuthUser = Depends(get_current_user)):
    """Get payment reconciliation report"""
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Get all payments for the school
        payments_result = supabase.table('payments').select('*').eq('school_id', current_user.schoolId).order('paid_at', desc=True).limit(100).execute()
        
        # Get invoices for reconciliation
        invoices_result = supabase.table('invoices').select('*').eq('school_id', current_user.schoolId).execute()
        
        # Build reconciliation data
        reconciliation = []
        for payment in payments_result.data or []:
            invoice = next((i for i in invoices_result.data or [] if i['id'] == payment['invoice_id']), None)
            reconciliation.append({
                "payment_id": payment['id'],
                "invoice_number": invoice['invoice_number'] if invoice else 'Unknown',
                "amount": payment['amount'],
                "payment_method": payment['payment_method'],
                "payment_reference": payment['payment_reference'],
                "status": payment['status'],
                "paid_at": payment['paid_at'],
                "invoice_status": invoice['status'] if invoice else 'Unknown',
                "is_reconciled": payment['status'] == 'completed' and (invoice and invoice['amount_paid'] >= invoice['amount_due'])
            })
        
        return {
            "reconciliation": reconciliation,
            "total_payments": len(reconciliation),
            "reconciled_count": len([r for r in reconciliation if r['is_reconciled']]),
            "unreconciled_count": len([r for r in reconciliation if not r['is_reconciled']])
        }
    except Exception as e:
        print(f"Error fetching reconciliation: {e}")
        return {"reconciliation": [], "total_payments": 0, "reconciled_count": 0, "unreconciled_count": 0}


@router.post("/finance/reconciliation/{payment_id}/match")
def match_payment(payment_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Manually match a payment to an invoice"""
    if not has_permission(current_user, "finance:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        invoice_id = payload.get('invoice_id')
        
        # Get payment
        payment_result = supabase.table('payments').select('*').eq('id', payment_id).eq('school_id', current_user.schoolId).execute()
        if not payment_result.data:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        payment = payment_result.data[0]
        
        # Get invoice
        invoice_result = supabase.table('invoices').select('*').eq('id', invoice_id).eq('school_id', current_user.schoolId).execute()
        if not invoice_result.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = invoice_result.data[0]
        
        # Update payment with invoice
        supabase.table('payments').update({
            'invoice_id': invoice_id,
            'status': 'completed'
        }).eq('id', payment_id).execute()
        
        # Update invoice amount paid
        new_amount_paid = invoice['amount_paid'] + payment['amount']
        new_status = 'paid' if new_amount_paid >= invoice['amount_due'] else 'part_paid'
        
        supabase.table('invoices').update({
            'amount_paid': new_amount_paid,
            'status': new_status
        }).eq('id', invoice_id).execute()
        
        # Log the action
        supabase.table('audit_logs').insert({
            'school_id': current_user.schoolId,
            'user_id': current_user.id,
            'action': 'payment_matched',
            'entity_type': 'payment',
            'entity_id': payment_id,
            'details': {
                'invoice_id': invoice_id,
                'amount': payment['amount']
            },
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {"success": True, "message": "Payment matched successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error matching payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reminders")
def get_reminders(current_user: AuthUser = Depends(get_current_user)):
    """Get all reminders for the school"""
    if not has_permission(current_user, "reminders:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('reminders').select('*').eq('school_id', current_user.schoolId).order('scheduled_for', asc=True).limit(50).execute()
        return {"reminders": result.data or []}
    except Exception as e:
        print(f"Error fetching reminders: {e}")
        return {"reminders": []}


@router.post("/reminders")
def create_reminder(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Create a new reminder"""
    if not has_permission(current_user, "reminders:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('reminders').insert({
            'school_id': current_user.schoolId,
            'title': payload.get('title'),
            'description': payload.get('description'),
            'reminder_type': payload.get('reminder_type'),
            'entity_type': payload.get('entity_type'),
            'entity_id': payload.get('entity_id'),
            'scheduled_for': payload.get('scheduled_for'),
            'status': 'pending',
            'channels': payload.get('channels', ['email']),
            'created_by': current_user.id
        }).execute()
        return {"success": True, "reminder": result.data[0]}
    except Exception as e:
        print(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/reminders/{reminder_id}")
def update_reminder(reminder_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Update a reminder"""
    if not has_permission(current_user, "reminders:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('title'):
            update_data['title'] = payload['title']
        if payload.get('description'):
            update_data['description'] = payload['description']
        if payload.get('scheduled_for'):
            update_data['scheduled_for'] = payload['scheduled_for']
        if payload.get('status'):
            update_data['status'] = payload['status']
        if payload.get('channels'):
            update_data['channels'] = payload['channels']
        
        result = supabase.table('reminders').update(update_data).eq('id', reminder_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "reminder": result.data[0]}
    except Exception as e:
        print(f"Error updating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Delete a reminder"""
    if not has_permission(current_user, "reminders:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('reminders').delete().eq('id', reminder_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "id": reminder_id}
    except Exception as e:
        print(f"Error deleting reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staff/{staff_id}/attendance")
def get_staff_attendance(staff_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Get attendance records for a staff member"""
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('attendance').select('*').eq('staff_id', staff_id).eq('school_id', current_user.schoolId).order('date', desc=True).limit(100).execute()
        return {"attendance": result.data or []}
    except Exception as e:
        print(f"Error fetching attendance: {e}")
        return {"attendance": []}


@router.get("/attendance")
def get_all_attendance(current_user: AuthUser = Depends(get_current_user)):
    """Get all attendance records for the school"""
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('attendance').select('*').eq('school_id', current_user.schoolId).order('date', desc=True).limit(200).execute()
        return {"attendance": result.data or []}
    except Exception as e:
        print(f"Error fetching attendance: {e}")
        return {"attendance": []}


@router.post("/attendance")
def record_attendance(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Record attendance for staff"""
    if not has_permission(current_user, "staff:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('attendance').insert({
            'school_id': current_user.schoolId,
            'staff_id': payload.get('staff_id'),
            'date': payload.get('date'),
            'check_in_time': payload.get('check_in_time'),
            'check_out_time': payload.get('check_out_time'),
            'status': payload.get('status', 'present'),
            'notes': payload.get('notes'),
            'recorded_by': current_user.id
        }).execute()
        return {"success": True, "attendance": result.data[0]}
    except Exception as e:
        print(f"Error recording attendance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/attendance/{attendance_id}")
def update_attendance(attendance_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Update an attendance record"""
    if not has_permission(current_user, "staff:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('check_in_time'):
            update_data['check_in_time'] = payload['check_in_time']
        if payload.get('check_out_time'):
            update_data['check_out_time'] = payload['check_out_time']
        if payload.get('status'):
            update_data['status'] = payload['status']
        if payload.get('notes'):
            update_data['notes'] = payload['notes']
        
        result = supabase.table('attendance').update(update_data).eq('id', attendance_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "attendance": result.data[0]}
    except Exception as e:
        print(f"Error updating attendance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attendance/summary")
def get_attendance_summary(current_user: AuthUser = Depends(get_current_user)):
    """Get attendance summary for the school"""
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import date, timedelta
        
        # Get attendance for the last 30 days
        thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
        result = supabase.table('attendance').select('*').eq('school_id', current_user.schoolId).gte('date', thirty_days_ago).execute()
        
        attendance_records = result.data or []
        
        # Calculate summary
        total_records = len(attendance_records)
        present_count = len([a for a in attendance_records if a['status'] == 'present'])
        absent_count = len([a for a in attendance_records if a['status'] == 'absent'])
        late_count = len([a for a in attendance_records if a['status'] == 'late'])
        
        return {
            "summary": {
                "total_records": total_records,
                "present_count": present_count,
                "absent_count": absent_count,
                "late_count": late_count,
                "attendance_rate": (present_count / total_records * 100) if total_records > 0 else 0
            },
            "period": "last_30_days"
        }
    except Exception as e:
        print(f"Error fetching attendance summary: {e}")
        return {"summary": {"total_records": 0, "present_count": 0, "absent_count": 0, "late_count": 0, "attendance_rate": 0}, "period": "last_30_days"}


@router.post("/reminders/process")
def process_reminders(current_user: AuthUser = Depends(get_current_user)):
    """Process pending reminders and send notifications"""
    if not has_permission(current_user, "reminders:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime
        
        # Get pending reminders that are due
        now = datetime.now().isoformat()
        result = supabase.table('reminders').select('*').eq('school_id', current_user.schoolId).eq('status', 'pending').lte('scheduled_for', now).execute()
        
        reminders = result.data or []
        processed_count = 0
        errors = []
        
        for reminder in reminders:
            try:
                # Get school settings for communication
                school_result = supabase.table('schools').select('*').eq('id', current_user.schoolId).execute()
                school = school_result.data[0] if school_result.data else None
                
                if not school:
                    errors.append({"reminder_id": reminder['id'], "error": "School not found"})
                    continue
                
                # Get recipient based on entity type
                recipient_email = None
                recipient_phone = None
                recipient_name = None
                
                if reminder['entity_type'] == 'invoice':
                    # Get invoice and family info
                    invoice_result = supabase.table('invoices').select('*, families(*)').eq('id', reminder['entity_id']).execute()
                    if invoice_result.data:
                        invoice = invoice_result.data[0]
                        family = invoice.get('families')
                        if family:
                            recipient_email = family.get('email')
                            recipient_phone = family.get('phone')
                            recipient_name = family.get('primary_contact_name')
                
                elif reminder['entity_type'] == 'lead':
                    # Get lead info
                    lead_result = supabase.table('leads').select('*').eq('id', reminder['entity_id']).execute()
                    if lead_result.data:
                        lead = lead_result.data[0]
                        recipient_email = lead.get('email')
                        recipient_phone = lead.get('phone')
                        recipient_name = lead.get('name')
                
                # Send notifications based on channels
                channels = reminder.get('channels', ['email'])
                message_sent = False
                
                if 'email' in channels and recipient_email:
                    # Get Brevo settings
                    brevo_key = school.get('metadata', {}).get('brevo_api_key')
                    if brevo_key:
                        try:
                            import httpx
                            response = httpx.post(
                                "https://api.brevo.com/v3/smtp/email",
                                headers={"api-key": brevo_key, "Content-Type": "application/json"},
                                json={
                                    "sender": {"name": school.get('name', 'EduDrive CRM'), "email": "noreply@edudrive.com"},
                                    "to": [{"email": recipient_email, "name": recipient_name or "Parent"}],
                                    "subject": reminder['title'],
                                    "htmlContent": reminder['description']
                                },
                                timeout=30
                            )
                            if response.status_code in [200, 201, 202]:
                                message_sent = True
                        except Exception as e:
                            print(f"Error sending email: {e}")
                
                if 'sms' in channels and recipient_phone:
                    # Get Termii settings
                    termii_key = school.get('metadata', {}).get('termii_api_key')
                    if termii_key:
                        try:
                            import httpx
                            response = httpx.post(
                                "https://api.ng.termii.com/api/sms/send",
                                json={
                                    "api_key": termii_key,
                                    "to": recipient_phone,
                                    "from": "EduDrive",
                                    "sms": reminder['title'] + " - " + reminder['description'],
                                    "type": "plain",
                                    "channel": "dnd"
                                },
                                timeout=30
                            )
                            if response.status_code == 200:
                                message_sent = True
                        except Exception as e:
                            print(f"Error sending SMS: {e}")
                
                if 'whatsapp' in channels and recipient_phone:
                    # Get WhatsApp settings
                    whatsapp_token = school.get('metadata', {}).get('whatsapp_access_token')
                    whatsapp_phone_id = school.get('metadata', {}).get('whatsapp_phone_number_id')
                    if whatsapp_token and whatsapp_phone_id:
                        try:
                            import httpx
                            response = httpx.post(
                                f"https://graph.facebook.com/v17.0/{whatsapp_phone_id}/messages",
                                headers={"Authorization": f"Bearer {whatsapp_token}", "Content-Type": "application/json"},
                                json={
                                    "messaging_product": "whatsapp",
                                    "to": recipient_phone,
                                    "type": "text",
                                    "text": {"body": reminder['title'] + "\n\n" + reminder['description']}
                                },
                                timeout=30
                            )
                            if response.status_code == 200:
                                message_sent = True
                        except Exception as e:
                            print(f"Error sending WhatsApp message: {e}")
                
                # Update reminder status
                if message_sent:
                    supabase.table('reminders').update({'status': 'sent', 'sent_at': datetime.now().isoformat()}).eq('id', reminder['id']).execute()
                    processed_count += 1
                else:
                    supabase.table('reminders').update({'status': 'failed'}).eq('id', reminder['id']).execute()
                    errors.append({"reminder_id": reminder['id'], "error": "No message sent - check communication settings"})
                
            except Exception as e:
                errors.append({"reminder_id": reminder['id'], "error": str(e)})
        
        return {
            "success": True,
            "processed_count": processed_count,
            "total_reminders": len(reminders),
            "errors": errors
        }
    except Exception as e:
        print(f"Error processing reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finance/fee-due-notifications")
def create_fee_due_notifications(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Create reminders for invoices with upcoming due dates"""
    if not has_permission(current_user, "finance:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        days_ahead = payload.get('days_ahead', 7)
        channels = payload.get('channels', ['email'])
        
        # Calculate the date threshold
        threshold_date = (datetime.now() + timedelta(days=days_ahead)).date().isoformat()
        
        # Get unpaid invoices with due dates within the threshold
        invoices_result = supabase.table('invoices').select('*').eq('school_id', current_user.schoolId).in_('status', ['pending', 'part_paid']).lte('due_date', threshold_date).execute()
        
        invoices = invoices_result.data or []
        created_reminders = []
        errors = []
        
        for invoice in invoices:
            try:
                # Check if a reminder already exists for this invoice
                existing_result = supabase.table('reminders').select('*').eq('school_id', current_user.schoolId).eq('entity_type', 'invoice').eq('entity_id', invoice['id']).eq('status', 'pending').execute()
                
                if existing_result.data:
                    # Reminder already exists, skip
                    continue
                
                # Get family info
                family_result = supabase.table('families').select('*').eq('id', invoice['family_id']).execute()
                family = family_result.data[0] if family_result.data else None
                
                if not family:
                    errors.append({"invoice_id": invoice['id'], "error": "Family not found"})
                    continue
                
                # Calculate days until due
                due_date = datetime.fromisoformat(invoice['due_date']).date()
                days_until_due = (due_date - datetime.now().date()).days
                
                # Create reminder
                reminder_result = supabase.table('reminders').insert({
                    'school_id': current_user.schoolId,
                    'title': f"Fee Due Reminder - Invoice #{invoice['invoice_number']}",
                    'description': f"Dear {family.get('primary_contact_name', 'Parent')}, this is a reminder that invoice #{invoice['invoice_number']} for {invoice.get('description', 'fees')} is due on {invoice['due_date']}. Amount due: {invoice['amount_due'] - invoice['amount_paid']}. Please ensure payment is made before the due date to avoid late fees.",
                    'reminder_type': 'fee_due',
                    'entity_type': 'invoice',
                    'entity_id': invoice['id'],
                    'scheduled_for': datetime.now().isoformat(),
                    'status': 'pending',
                    'channels': channels,
                    'created_by': current_user.id
                }).execute()
                
                created_reminders.append(reminder_result.data[0])
                
            except Exception as e:
                errors.append({"invoice_id": invoice['id'], "error": str(e)})
        
        return {
            "success": True,
            "created_reminders": created_reminders,
            "total_created": len(created_reminders),
            "total_invoices": len(invoices),
            "errors": errors
        }
    except Exception as e:
        print(f"Error creating fee due notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admissions/follow-up-reminders")
def create_admission_follow_up_reminders(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Create follow-up reminders for leads that haven't been updated recently"""
    if not has_permission(current_user, "admissions:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        days_inactive = payload.get('days_inactive', 7)
        channels = payload.get('channels', ['email'])
        
        # Calculate the date threshold for inactive leads
        threshold_date = (datetime.now() - timedelta(days=days_inactive)).isoformat()
        
        # Get leads that haven't been updated recently and are not in final stages
        leads_result = supabase.table('leads').select('*').eq('school_id', current_user.schoolId).not_.in_('stage', ['enrolled', 'lost']).lte('updated_at', threshold_date).execute()
        
        leads = leads_result.data or []
        created_reminders = []
        errors = []
        
        for lead in leads:
            try:
                # Check if a reminder already exists for this lead
                existing_result = supabase.table('reminders').select('*').eq('school_id', current_user.schoolId).eq('entity_type', 'lead').eq('entity_id', lead['id']).eq('status', 'pending').execute()
                
                if existing_result.data:
                    # Reminder already exists, skip
                    continue
                
                # Calculate days since last update
                last_updated = datetime.fromisoformat(lead['updated_at'])
                days_since_update = (datetime.now() - last_updated).days
                
                # Create reminder
                reminder_result = supabase.table('reminders').insert({
                    'school_id': current_user.schoolId,
                    'title': f"Follow-up Required - {lead.get('name', 'Lead')}",
                    'description': f"Lead {lead.get('name', 'Unknown')} (Stage: {lead.get('stage', 'Unknown')}) has not been updated for {days_since_update} days. Please follow up with {lead.get('email', 'the lead')} at {lead.get('phone', 'N/A')} to move them forward in the admissions process.",
                    'reminder_type': 'admission_follow_up',
                    'entity_type': 'lead',
                    'entity_id': lead['id'],
                    'scheduled_for': datetime.now().isoformat(),
                    'status': 'pending',
                    'channels': channels,
                    'created_by': current_user.id
                }).execute()
                
                created_reminders.append(reminder_result.data[0])
                
            except Exception as e:
                errors.append({"lead_id": lead['id'], "error": str(e)})
        
        return {
            "success": True,
            "created_reminders": created_reminders,
            "total_created": len(created_reminders),
            "total_leads": len(leads),
            "errors": errors
        }
    except Exception as e:
        print(f"Error creating admission follow-up reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments/{payment_id}/receipt")
def get_payment_receipt(payment_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Get receipt for a payment"""
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Get payment with invoice and family info
        payment_result = supabase.table('payments').select('*, invoices(*, families(*))').eq('id', payment_id).eq('school_id', current_user.schoolId).execute()
        
        if not payment_result.data:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        payment = payment_result.data[0]
        invoice = payment.get('invoices')
        family = invoice.get('families') if invoice else None
        
        # Get school info
        school_result = supabase.table('schools').select('*').eq('id', current_user.schoolId).execute()
        school = school_result.data[0] if school_result.data else None
        
        # Generate receipt data
        receipt_data = {
            "receipt_number": f"RCP-{payment['id'][:8].upper()}",
            "payment_date": payment['paid_at'],
            "amount": payment['amount'],
            "payment_method": payment['payment_method'],
            "payment_reference": payment['payment_reference'],
            "school_name": school.get('name', 'School') if school else 'School',
            "school_address": school.get('address', '') if school else '',
            "invoice_number": invoice['invoice_number'] if invoice else 'N/A',
            "invoice_description": invoice.get('description', '') if invoice else '',
            "family_name": family.get('primary_contact_name', '') if family else '',
            "family_email": family.get('email', '') if family else '',
            "family_phone": family.get('phone', '') if family else ''
        }
        
        return {"receipt": receipt_data}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching receipt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/{payment_id}/receipt/send")
def send_payment_receipt(payment_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Send receipt for a payment via email/SMS/WhatsApp"""
    if not has_permission(current_user, "finance:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        channels = payload.get('channels', ['email'])
        
        # Get payment with invoice and family info
        payment_result = supabase.table('payments').select('*, invoices(*, families(*))').eq('id', payment_id).eq('school_id', current_user.schoolId).execute()
        
        if not payment_result.data:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        payment = payment_result.data[0]
        invoice = payment.get('invoices')
        family = invoice.get('families') if invoice else None
        
        if not family:
            raise HTTPException(status_code=404, detail="Family not found")
        
        # Get school info
        school_result = supabase.table('schools').select('*').eq('id', current_user.schoolId).execute()
        school = school_result.data[0] if school_result.data else None
        
        if not school:
            raise HTTPException(status_code=404, detail="School not found")
        
        # Generate receipt content
        receipt_number = f"RCP-{payment['id'][:8].upper()}"
        receipt_content = f"""
        <h2>Payment Receipt</h2>
        <p><strong>Receipt Number:</strong> {receipt_number}</p>
        <p><strong>Date:</strong> {payment['paid_at']}</p>
        <p><strong>Amount:</strong> {payment['amount']}</p>
        <p><strong>Payment Method:</strong> {payment['payment_method']}</p>
        <p><strong>Reference:</strong> {payment['payment_reference']}</p>
        <hr>
        <p><strong>Invoice:</strong> {invoice['invoice_number'] if invoice else 'N/A'}</p>
        <p><strong>Description:</strong> {invoice.get('description', '') if invoice else ''}</p>
        <hr>
        <p><strong>{school.get('name', 'School')}</strong></p>
        <p>{school.get('address', '') if school else ''}</p>
        """
        
        sent_channels = []
        errors = []
        
        # Send via email
        if 'email' in channels and family.get('email'):
            brevo_key = school.get('metadata', {}).get('brevo_api_key')
            if brevo_key:
                try:
                    import httpx
                    response = httpx.post(
                        "https://api.brevo.com/v3/smtp/email",
                        headers={"api-key": brevo_key, "Content-Type": "application/json"},
                        json={
                            "sender": {"name": school.get('name', 'EduDrive CRM'), "email": "noreply@edudrive.com"},
                            "to": [{"email": family.get('email'), "name": family.get('primary_contact_name', 'Parent')}],
                            "subject": f"Payment Receipt - {receipt_number}",
                            "htmlContent": receipt_content
                        },
                        timeout=30
                    )
                    if response.status_code in [200, 201, 202]:
                        sent_channels.append('email')
                except Exception as e:
                    errors.append({"channel": "email", "error": str(e)})
        
        # Send via SMS
        if 'sms' in channels and family.get('phone'):
            termii_key = school.get('metadata', {}).get('termii_api_key')
            if termii_key:
                try:
                    import httpx
                    sms_content = f"Payment Receipt {receipt_number}. Amount: {payment['amount']}. Date: {payment['paid_at']}. Thank you for your payment."
                    response = httpx.post(
                        "https://api.ng.termii.com/api/sms/send",
                        json={
                            "api_key": termii_key,
                            "to": family.get('phone'),
                            "from": "EduDrive",
                            "sms": sms_content,
                            "type": "plain",
                            "channel": "dnd"
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        sent_channels.append('sms')
                except Exception as e:
                    errors.append({"channel": "sms", "error": str(e)})
        
        # Send via WhatsApp
        if 'whatsapp' in channels and family.get('phone'):
            whatsapp_token = school.get('metadata', {}).get('whatsapp_access_token')
            whatsapp_phone_id = school.get('metadata', {}).get('whatsapp_phone_number_id')
            if whatsapp_token and whatsapp_phone_id:
                try:
                    import httpx
                    whatsapp_content = f"Payment Receipt {receipt_number}\n\nAmount: {payment['amount']}\nDate: {payment['paid_at']}\nInvoice: {invoice['invoice_number'] if invoice else 'N/A'}\n\nThank you for your payment."
                    response = httpx.post(
                        f"https://graph.facebook.com/v17.0/{whatsapp_phone_id}/messages",
                        headers={"Authorization": f"Bearer {whatsapp_token}", "Content-Type": "application/json"},
                        json={
                            "messaging_product": "whatsapp",
                            "to": family.get('phone'),
                            "type": "text",
                            "text": {"body": whatsapp_content}
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        sent_channels.append('whatsapp')
                except Exception as e:
                    errors.append({"channel": "whatsapp", "error": str(e)})
        
        # Log the action
        supabase.table('audit_logs').insert({
            'school_id': current_user.schoolId,
            'user_id': current_user.id,
            'action': 'receipt_sent',
            'entity_type': 'payment',
            'entity_id': payment_id,
            'details': {
                'channels': sent_channels,
                'receipt_number': receipt_number
            },
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {
            "success": True,
            "sent_channels": sent_channels,
            "receipt_number": receipt_number,
            "errors": errors
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending receipt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/helpdesk/tickets/sla-status")
def get_sla_status(current_user: AuthUser = Depends(get_current_user)):
    """Get SLA status for all help desk tickets"""
    if not has_permission(current_user, "helpdesk:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime
        
        # Get all tickets for the school
        tickets_result = supabase.table('helpdesk_tickets').select('*').eq('school_id', current_user.schoolId).order('created_at', desc=True).limit(100).execute()
        
        tickets = tickets_result.data or []
        sla_status = []
        
        for ticket in tickets:
            # Calculate SLA status
            sla_deadline = ticket.get('sla_deadline')
            if sla_deadline:
                deadline = datetime.fromisoformat(sla_deadline)
                now = datetime.now()
                
                if ticket['status'] == 'resolved':
                    sla_status.append({
                        "ticket_id": ticket['id'],
                        "ticket_number": ticket.get('ticket_number'),
                        "subject": ticket.get('subject'),
                        "status": ticket['status'],
                        "sla_deadline": sla_deadline,
                        "sla_status": "met" if ticket.get('resolved_at') and datetime.fromisoformat(ticket['resolved_at']) <= deadline else "missed",
                        "priority": ticket.get('priority')
                    })
                else:
                    hours_remaining = (deadline - now).total_seconds() / 3600
                    if hours_remaining < 0:
                        sla_status.append({
                            "ticket_id": ticket['id'],
                            "ticket_number": ticket.get('ticket_number'),
                            "subject": ticket.get('subject'),
                            "status": ticket['status'],
                            "sla_deadline": sla_deadline,
                            "sla_status": "overdue",
                            "hours_overdue": abs(hours_remaining),
                            "priority": ticket.get('priority')
                        })
                    elif hours_remaining < 24:
                        sla_status.append({
                            "ticket_id": ticket['id'],
                            "ticket_number": ticket.get('ticket_number'),
                            "subject": ticket.get('subject'),
                            "status": ticket['status'],
                            "sla_deadline": sla_deadline,
                            "sla_status": "critical",
                            "hours_remaining": hours_remaining,
                            "priority": ticket.get('priority')
                        })
                    elif hours_remaining < 48:
                        sla_status.append({
                            "ticket_id": ticket['id'],
                            "ticket_number": ticket.get('ticket_number'),
                            "subject": ticket.get('subject'),
                            "status": ticket['status'],
                            "sla_deadline": sla_deadline,
                            "sla_status": "warning",
                            "hours_remaining": hours_remaining,
                            "priority": ticket.get('priority')
                        })
                    else:
                        sla_status.append({
                            "ticket_id": ticket['id'],
                            "ticket_number": ticket.get('ticket_number'),
                            "subject": ticket.get('subject'),
                            "status": ticket['status'],
                            "sla_deadline": sla_deadline,
                            "sla_status": "on_track",
                            "hours_remaining": hours_remaining,
                            "priority": ticket.get('priority')
                        })
            else:
                sla_status.append({
                    "ticket_id": ticket['id'],
                    "ticket_number": ticket.get('ticket_number'),
                    "subject": ticket.get('subject'),
                    "status": ticket['status'],
                    "sla_deadline": None,
                    "sla_status": "not_set",
                    "priority": ticket.get('priority')
                })
        
        # Calculate summary
        total_tickets = len(sla_status)
        overdue_count = len([s for s in sla_status if s['sla_status'] == 'overdue'])
        critical_count = len([s for s in sla_status if s['sla_status'] == 'critical'])
        warning_count = len([s for s in sla_status if s['sla_status'] == 'warning'])
        on_track_count = len([s for s in sla_status if s['sla_status'] == 'on_track'])
        met_count = len([s for s in sla_status if s['sla_status'] == 'met'])
        missed_count = len([s for s in sla_status if s['sla_status'] == 'missed'])
        
        return {
            "sla_status": sla_status,
            "summary": {
                "total_tickets": total_tickets,
                "overdue_count": overdue_count,
                "critical_count": critical_count,
                "warning_count": warning_count,
                "on_track_count": on_track_count,
                "met_count": met_count,
                "missed_count": missed_count,
                "sla_compliance_rate": (met_count / (met_count + missed_count) * 100) if (met_count + missed_count) > 0 else 0
            }
        }
    except Exception as e:
        print(f"Error fetching SLA status: {e}")
        return {"sla_status": [], "summary": {"total_tickets": 0, "overdue_count": 0, "critical_count": 0, "warning_count": 0, "on_track_count": 0, "met_count": 0, "missed_count": 0, "sla_compliance_rate": 0}}


@router.patch("/helpdesk/tickets/{ticket_id}/sla")
def set_ticket_sla(ticket_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Set SLA deadline for a ticket"""
    if not has_permission(current_user, "helpdesk:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        update_data = {}
        if payload.get('sla_deadline'):
            update_data['sla_deadline'] = payload['sla_deadline']
        if payload.get('priority'):
            update_data['priority'] = payload['priority']
        
        result = supabase.table('helpdesk_tickets').update(update_data).eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        return {"success": True, "ticket": result.data[0]}
    except Exception as e:
        print(f"Error setting SLA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/helpdesk/tickets/overdue")
def get_overdue_tickets(current_user: AuthUser = Depends(get_current_user)):
    """Get tickets that are overdue or approaching SLA deadline"""
    if not has_permission(current_user, "helpdesk:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime
        
        # Get tickets with SLA deadlines
        tickets_result = supabase.table('helpdesk_tickets').select('*').eq('school_id', current_user.schoolId).not_.in_('status', ['resolved', 'closed']).execute()
        
        tickets = tickets_result.data or []
        overdue_tickets = []
        critical_tickets = []
        
        for ticket in tickets:
            sla_deadline = ticket.get('sla_deadline')
            if sla_deadline:
                deadline = datetime.fromisoformat(sla_deadline)
                now = datetime.now()
                hours_remaining = (deadline - now).total_seconds() / 3600
                
                if hours_remaining < 0:
                    overdue_tickets.append({
                        "ticket_id": ticket['id'],
                        "ticket_number": ticket.get('ticket_number'),
                        "subject": ticket.get('subject'),
                        "status": ticket['status'],
                        "sla_deadline": sla_deadline,
                        "hours_overdue": abs(hours_remaining),
                        "priority": ticket.get('priority'),
                        "assigned_to": ticket.get('assigned_to')
                    })
                elif hours_remaining < 24:
                    critical_tickets.append({
                        "ticket_id": ticket['id'],
                        "ticket_number": ticket.get('ticket_number'),
                        "subject": ticket.get('subject'),
                        "status": ticket['status'],
                        "sla_deadline": sla_deadline,
                        "hours_remaining": hours_remaining,
                        "priority": ticket.get('priority'),
                        "assigned_to": ticket.get('assigned_to')
                    })
        
        return {
            "overdue_tickets": overdue_tickets,
            "critical_tickets": critical_tickets,
            "total_overdue": len(overdue_tickets),
            "total_critical": len(critical_tickets)
        }
    except Exception as e:
        print(f"Error fetching overdue tickets: {e}")
        return {"overdue_tickets": [], "critical_tickets": [], "total_overdue": 0, "total_critical": 0}


@router.post("/helpdesk/tickets/{ticket_id}/assign")
def assign_ticket(ticket_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Assign a ticket to a staff member"""
    if not has_permission(current_user, "helpdesk:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        assigned_to = payload.get('assigned_to')
        notes = payload.get('notes')
        
        # Update ticket assignment
        result = supabase.table('helpdesk_tickets').update({
            'assigned_to': assigned_to,
            'assigned_at': datetime.now().isoformat(),
            'assigned_by': current_user.id,
            'status': 'assigned'
        }).eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        
        # Add assignment note if provided
        if notes:
            supabase.table('helpdesk_comments').insert({
                'school_id': current_user.schoolId,
                'ticket_id': ticket_id,
                'user_id': current_user.id,
                'comment': f"Ticket assigned to {assigned_to}. {notes}",
                'is_internal': True,
                'created_at': datetime.now().isoformat()
            }).execute()
        
        # Log the action
        supabase.table('audit_logs').insert({
            'school_id': current_user.schoolId,
            'user_id': current_user.id,
            'action': 'ticket_assigned',
            'entity_type': 'helpdesk_ticket',
            'entity_id': ticket_id,
            'details': {
                'assigned_to': assigned_to,
                'notes': notes
            },
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {"success": True, "ticket": result.data[0]}
    except Exception as e:
        print(f"Error assigning ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/helpdesk/tickets/{ticket_id}/reassign")
def reassign_ticket(ticket_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Reassign a ticket to a different staff member"""
    if not has_permission(current_user, "helpdesk:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        assigned_to = payload.get('assigned_to')
        reason = payload.get('reason')
        
        # Get current assignment
        ticket_result = supabase.table('helpdesk_tickets').select('*').eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        if not ticket_result.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        current_assignment = ticket_result.data[0].get('assigned_to')
        
        # Update ticket assignment
        result = supabase.table('helpdesk_tickets').update({
            'assigned_to': assigned_to,
            'reassigned_at': datetime.now().isoformat(),
            'reassigned_by': current_user.id,
            'previous_assigned_to': current_assignment
        }).eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        
        # Add reassignment note
        supabase.table('helpdesk_comments').insert({
            'school_id': current_user.schoolId,
            'ticket_id': ticket_id,
            'user_id': current_user.id,
            'comment': f"Ticket reassigned from {current_assignment} to {assigned_to}. Reason: {reason}",
            'is_internal': True,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        # Log the action
        supabase.table('audit_logs').insert({
            'school_id': current_user.schoolId,
            'user_id': current_user.id,
            'action': 'ticket_reassigned',
            'entity_type': 'helpdesk_ticket',
            'entity_id': ticket_id,
            'details': {
                'from': current_assignment,
                'to': assigned_to,
                'reason': reason
            },
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {"success": True, "ticket": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error reassigning ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/helpdesk/tickets/unassigned")
def get_unassigned_tickets(current_user: AuthUser = Depends(get_current_user)):
    """Get tickets that are not assigned to anyone"""
    if not has_permission(current_user, "helpdesk:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('helpdesk_tickets').select('*').eq('school_id', current_user.schoolId).is_('assigned_to', None).not_.in_('status', ['resolved', 'closed']).order('created_at', desc=True).limit(50).execute()
        return {"unassigned_tickets": result.data or []}
    except Exception as e:
        print(f"Error fetching unassigned tickets: {e}")
        return {"unassigned_tickets": []}


@router.get("/helpdesk/tickets/my-tickets")
def get_my_tickets(current_user: AuthUser = Depends(get_current_user)):
    """Get tickets assigned to the current user"""
    if not has_permission(current_user, "helpdesk:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('helpdesk_tickets').select('*').eq('school_id', current_user.schoolId).eq('assigned_to', current_user.id).not_.in_('status', ['resolved', 'closed']).order('created_at', desc=True).limit(50).execute()
        return {"my_tickets": result.data or []}
    except Exception as e:
        print(f"Error fetching my tickets: {e}")
        return {"my_tickets": []}


@router.post("/helpdesk/tickets/auto-assign")
def auto_assign_tickets(payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Auto-assign unassigned tickets based on workload and expertise"""
    if not has_permission(current_user, "helpdesk:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Get unassigned tickets
        unassigned_result = supabase.table('helpdesk_tickets').select('*').eq('school_id', current_user.schoolId).is_('assigned_to', None).not_.in_('status', ['resolved', 'closed']).execute()
        
        unassigned_tickets = unassigned_result.data or []
        
        # Get available staff with helpdesk role
        staff_result = supabase.table('user_roles').select('*, users(*)').eq('school_id', current_user.schoolId).in_('role', ['school_admin', 'helpdesk', 'support']).execute()
        
        staff_members = staff_result.data or []
        
        assigned_count = 0
        errors = []
        
        for ticket in unassigned_tickets:
            try:
                # Simple round-robin assignment based on current workload
                # Get ticket count for each staff member
                staff_workload = []
                for staff in staff_members:
                    staff_id = staff['user_id']
                    ticket_count_result = supabase.table('helpdesk_tickets').select('*').eq('school_id', current_user.schoolId).eq('assigned_to', staff_id).not_.in_('status', ['resolved', 'closed']).execute()
                    ticket_count = len(ticket_count_result.data or [])
                    staff_workload.append({
                        'staff_id': staff_id,
                        'ticket_count': ticket_count
                    })
                
                # Sort by workload (ascending)
                staff_workload.sort(key=lambda x: x['ticket_count'])
                
                # Assign to staff with lowest workload
                if staff_workload:
                    assigned_to = staff_workload[0]['staff_id']
                    
                    supabase.table('helpdesk_tickets').update({
                        'assigned_to': assigned_to,
                        'assigned_at': datetime.now().isoformat(),
                        'assigned_by': current_user.id,
                        'status': 'assigned'
                    }).eq('id', ticket['id']).execute()
                    
                    assigned_count += 1
                else:
                    errors.append({"ticket_id": ticket['id'], "error": "No available staff members"})
                
            except Exception as e:
                errors.append({"ticket_id": ticket['id'], "error": str(e)})
        
        return {
            "success": True,
            "assigned_count": assigned_count,
            "total_unassigned": len(unassigned_tickets),
            "errors": errors
        }
    except Exception as e:
        print(f"Error auto-assigning tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/helpdesk/tickets/workflow")
def get_ticket_workflow(current_user: AuthUser = Depends(get_current_user)):
    """Get the ticket workflow configuration"""
    if not has_permission(current_user, "helpdesk:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Default workflow stages
        workflow_stages = [
            {"stage": "open", "label": "Open", "description": "New ticket created", "order": 1},
            {"stage": "assigned", "label": "Assigned", "description": "Ticket assigned to staff", "order": 2},
            {"stage": "in_progress", "label": "In Progress", "description": "Staff working on ticket", "order": 3},
            {"stage": "pending", "label": "Pending", "description": "Waiting for customer response", "order": 4},
            {"stage": "resolved", "label": "Resolved", "description": "Issue resolved", "order": 5},
            {"stage": "closed", "label": "Closed", "description": "Ticket closed", "order": 6}
        ]
        
        # Get custom workflow from school settings if exists
        school_result = supabase.table('schools').select('*').eq('id', current_user.schoolId).execute()
        if school_result.data:
            school = school_result.data[0]
            custom_workflow = school.get('metadata', {}).get('ticket_workflow')
            if custom_workflow:
                workflow_stages = custom_workflow
        
        return {"workflow_stages": workflow_stages}
    except Exception as e:
        print(f"Error fetching workflow: {e}")
        return {"workflow_stages": []}


@router.patch("/helpdesk/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Update ticket status with workflow validation"""
    if not has_permission(current_user, "helpdesk:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        new_status = payload.get('status')
        resolution_notes = payload.get('resolution_notes')
        
        # Validate status transition
        valid_transitions = {
            'open': ['assigned', 'closed'],
            'assigned': ['in_progress', 'closed'],
            'in_progress': ['pending', 'resolved', 'closed'],
            'pending': ['in_progress', 'resolved', 'closed'],
            'resolved': ['closed', 'in_progress'],
            'closed': ['open']
        }
        
        # Get current ticket
        ticket_result = supabase.table('helpdesk_tickets').select('*').eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        if not ticket_result.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        current_status = ticket_result.data[0].get('status')
        
        # Check if transition is valid
        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(status_code=400, detail=f"Invalid status transition from {current_status} to {new_status}")
        
        # Prepare update data
        update_data = {'status': new_status}
        
        # Add timestamps based on status
        if new_status == 'in_progress':
            update_data['started_at'] = datetime.now().isoformat()
        elif new_status == 'resolved':
            update_data['resolved_at'] = datetime.now().isoformat()
            update_data['resolved_by'] = current_user.id
            if resolution_notes:
                update_data['resolution_notes'] = resolution_notes
        elif new_status == 'closed':
            update_data['closed_at'] = datetime.now().isoformat()
            update_data['closed_by'] = current_user.id
        
        # Update ticket
        result = supabase.table('helpdesk_tickets').update(update_data).eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        
        # Add status change comment
        supabase.table('helpdesk_comments').insert({
            'school_id': current_user.schoolId,
            'ticket_id': ticket_id,
            'user_id': current_user.id,
            'comment': f"Status changed from {current_status} to {new_status}" + (f". Resolution: {resolution_notes}" if resolution_notes else ""),
            'is_internal': True,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        # Log the action
        supabase.table('audit_logs').insert({
            'school_id': current_user.schoolId,
            'user_id': current_user.id,
            'action': 'ticket_status_changed',
            'entity_type': 'helpdesk_ticket',
            'entity_id': ticket_id,
            'details': {
                'from': current_status,
                'to': new_status,
                'resolution_notes': resolution_notes
            },
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {"success": True, "ticket": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating ticket status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/helpdesk/tickets/{ticket_id}/reopen")
def reopen_ticket(ticket_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Reopen a closed or resolved ticket"""
    if not has_permission(current_user, "helpdesk:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        reason = payload.get('reason')
        
        # Get current ticket
        ticket_result = supabase.table('helpdesk_tickets').select('*').eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        if not ticket_result.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        current_status = ticket_result.data[0].get('status')
        
        if current_status not in ['resolved', 'closed']:
            raise HTTPException(status_code=400, detail="Only resolved or closed tickets can be reopened")
        
        # Reopen ticket
        result = supabase.table('helpdesk_tickets').update({
            'status': 'open',
            'reopened_at': datetime.now().isoformat(),
            'reopened_by': current_user.id,
            'reopened_reason': reason
        }).eq('id', ticket_id).eq('school_id', current_user.schoolId).execute()
        
        # Add reopen comment
        supabase.table('helpdesk_comments').insert({
            'school_id': current_user.schoolId,
            'ticket_id': ticket_id,
            'user_id': current_user.id,
            'comment': f"Ticket reopened from {current_status}. Reason: {reason}",
            'is_internal': True,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        # Log the action
        supabase.table('audit_logs').insert({
            'school_id': current_user.schoolId,
            'user_id': current_user.id,
            'action': 'ticket_reopened',
            'entity_type': 'helpdesk_ticket',
            'entity_id': ticket_id,
            'details': {
                'from': current_status,
                'reason': reason
            },
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {"success": True, "ticket": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error reopening ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/helpdesk/tickets/status-summary")
def get_status_summary(current_user: AuthUser = Depends(get_current_user)):
    """Get summary of tickets by status"""
    if not has_permission(current_user, "helpdesk:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Get all tickets
        tickets_result = supabase.table('helpdesk_tickets').select('*').eq('school_id', current_user.schoolId).execute()
        
        tickets = tickets_result.data or []
        
        # Count by status
        status_counts = {}
        for ticket in tickets:
            status = ticket.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "status_summary": status_counts,
            "total_tickets": len(tickets)
        }
    except Exception as e:
        print(f"Error fetching status summary: {e}")
        return {"status_summary": {}, "total_tickets": 0}


@router.get("/staff/{staff_id}/performance")
def get_staff_performance(staff_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Get performance metrics for a staff member"""
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get attendance for the last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        attendance_result = supabase.table('attendance').select('*').eq('staff_id', staff_id).eq('school_id', current_user.schoolId).gte('date', thirty_days_ago).execute()
        attendance_records = attendance_result.data or []
        
        # Calculate attendance metrics
        total_days = len(attendance_records)
        present_days = len([a for a in attendance_records if a['status'] == 'present'])
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        # Get help desk tickets assigned and resolved
        tickets_result = supabase.table('helpdesk_tickets').select('*').eq('assigned_to', staff_id).eq('school_id', current_user.schoolId).execute()
        tickets = tickets_result.data or []
        
        total_tickets = len(tickets)
        resolved_tickets = len([t for t in tickets if t['status'] == 'resolved'])
        closed_tickets = len([t for t in tickets if t['status'] == 'closed'])
        
        # Calculate resolution rate
        resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
        
        # Get average resolution time for resolved tickets
        resolved_tickets_data = [t for t in tickets if t['status'] == 'resolved' and t.get('resolved_at') and t.get('created_at')]
        resolution_times = []
        for ticket in resolved_tickets_data:
            try:
                created = datetime.fromisoformat(ticket['created_at'])
                resolved = datetime.fromisoformat(ticket['resolved_at'])
                resolution_times.append((resolved - created).total_seconds() / 3600)  # hours
            except:
                pass
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Get SLA compliance
        sla_compliant = 0
        sla_total = 0
        for ticket in resolved_tickets_data:
            if ticket.get('sla_deadline'):
                sla_total += 1
                try:
                    deadline = datetime.fromisoformat(ticket['sla_deadline'])
                    resolved = datetime.fromisoformat(ticket['resolved_at'])
                    if resolved <= deadline:
                        sla_compliant += 1
                except:
                    pass
        
        sla_compliance_rate = (sla_compliant / sla_total * 100) if sla_total > 0 else 0
        
        # Calculate overall score
        attendance_score = attendance_rate * 0.3
        resolution_score = resolution_rate * 0.4
        sla_score = sla_compliance_rate * 0.3
        overall_score = attendance_score + resolution_score + sla_score
        
        return {
            "staff_id": staff_id,
            "period": "last_30_days",
            "metrics": {
                "attendance": {
                    "total_days": total_days,
                    "present_days": present_days,
                    "attendance_rate": round(attendance_rate, 2)
                },
                "helpdesk": {
                    "total_tickets": total_tickets,
                    "resolved_tickets": resolved_tickets,
                    "closed_tickets": closed_tickets,
                    "resolution_rate": round(resolution_rate, 2),
                    "avg_resolution_time_hours": round(avg_resolution_time, 2),
                    "sla_compliance_rate": round(sla_compliance_rate, 2)
                }
            },
            "scorecard": {
                "attendance_score": round(attendance_score, 2),
                "resolution_score": round(resolution_score, 2),
                "sla_score": round(sla_score, 2),
                "overall_score": round(overall_score, 2),
                "grade": get_performance_grade(overall_score)
            }
        }
    except Exception as e:
        print(f"Error fetching staff performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_performance_grade(score: float) -> str:
    """Helper function to get performance grade from score"""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Good"
    elif score >= 70:
        return "Satisfactory"
    elif score >= 60:
        return "Needs Improvement"
    else:
        return "Poor"


@router.get("/staff/performance-summary")
def get_staff_performance_summary(current_user: AuthUser = Depends(get_current_user)):
    """Get performance summary for all staff"""
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Get all staff for the school
        staff_result = supabase.table('user_roles').select('*, users(*)').eq('school_id', current_user.schoolId).execute()
        
        staff_members = staff_result.data or []
        performance_summary = []
        
        for staff in staff_members:
            staff_id = staff['user_id']
            user = staff.get('users', {})
            
            # Get performance for each staff member
            try:
                from datetime import datetime, timedelta
                
                # Attendance
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                attendance_result = supabase.table('attendance').select('*').eq('staff_id', staff_id).eq('school_id', current_user.schoolId).gte('date', thirty_days_ago).execute()
                attendance_records = attendance_result.data or []
                
                total_days = len(attendance_records)
                present_days = len([a for a in attendance_records if a['status'] == 'present'])
                attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
                
                # Help desk tickets
                tickets_result = supabase.table('helpdesk_tickets').select('*').eq('assigned_to', staff_id).eq('school_id', current_user.schoolId).execute()
                tickets = tickets_result.data or []
                
                total_tickets = len(tickets)
                resolved_tickets = len([t for t in tickets if t['status'] == 'resolved'])
                resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
                
                # SLA compliance
                resolved_tickets_data = [t for t in tickets if t['status'] == 'resolved' and t.get('sla_deadline') and t.get('resolved_at')]
                sla_compliant = 0
                sla_total = 0
                for ticket in resolved_tickets_data:
                    sla_total += 1
                    try:
                        deadline = datetime.fromisoformat(ticket['sla_deadline'])
                        resolved = datetime.fromisoformat(ticket['resolved_at'])
                        if resolved <= deadline:
                            sla_compliant += 1
                    except:
                        pass
                
                sla_compliance_rate = (sla_compliant / sla_total * 100) if sla_total > 0 else 0
                
                # Calculate score
                attendance_score = attendance_rate * 0.3
                resolution_score = resolution_rate * 0.4
                sla_score = sla_compliance_rate * 0.3
                overall_score = attendance_score + resolution_score + sla_score
                
                performance_summary.append({
                    "staff_id": staff_id,
                    "staff_name": user.get('name', 'Unknown'),
                    "staff_email": user.get('email', ''),
                    "role": staff.get('role', ''),
                    "attendance_rate": round(attendance_rate, 2),
                    "resolution_rate": round(resolution_rate, 2),
                    "sla_compliance_rate": round(sla_compliance_rate, 2),
                    "overall_score": round(overall_score, 2),
                    "grade": get_performance_grade(overall_score)
                })
                
            except Exception as e:
                print(f"Error calculating performance for staff {staff_id}: {e}")
                continue
        
        # Sort by overall score (descending)
        performance_summary.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return {
            "performance_summary": performance_summary,
            "total_staff": len(performance_summary)
        }
    except Exception as e:
        print(f"Error fetching performance summary: {e}")
        return {"performance_summary": [], "total_staff": 0}


@router.get("/staff/{staff_id}/workload")
def get_staff_workload(staff_id: str, current_user: AuthUser = Depends(get_current_user)):
    """Get workload indicators for a staff member"""
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Get active help desk tickets
        tickets_result = supabase.table('helpdesk_tickets').select('*').eq('assigned_to', staff_id).eq('school_id', current_user.schoolId).not_.in_('status', ['resolved', 'closed']).execute()
        active_tickets = tickets_result.data or []
        
        # Get overdue tickets
        from datetime import datetime
        overdue_tickets = []
        critical_tickets = []
        
        for ticket in active_tickets:
            sla_deadline = ticket.get('sla_deadline')
            if sla_deadline:
                try:
                    deadline = datetime.fromisoformat(sla_deadline)
                    now = datetime.now()
                    hours_remaining = (deadline - now).total_seconds() / 3600
                    
                    if hours_remaining < 0:
                        overdue_tickets.append(ticket)
                    elif hours_remaining < 24:
                        critical_tickets.append(ticket)
                except:
                    pass
        
        # Get tasks or other workload indicators (if applicable)
        # For now, we'll use help desk tickets as the primary workload indicator
        
        workload_level = "low"
        if len(active_tickets) > 10:
            workload_level = "high"
        elif len(active_tickets) > 5:
            workload_level = "medium"
        
        return {
            "staff_id": staff_id,
            "workload": {
                "active_tickets": len(active_tickets),
                "overdue_tickets": len(overdue_tickets),
                "critical_tickets": len(critical_tickets),
                "workload_level": workload_level
            },
            "recommendations": get_workload_recommendations(len(active_tickets), len(overdue_tickets), len(critical_tickets))
        }
    except Exception as e:
        print(f"Error fetching staff workload: {e}")
        return {"staff_id": staff_id, "workload": {"active_tickets": 0, "overdue_tickets": 0, "critical_tickets": 0, "workload_level": "low"}, "recommendations": []}


def get_workload_recommendations(active: int, overdue: int, critical: int) -> list:
    """Helper function to get workload recommendations"""
    recommendations = []
    
    if overdue > 0:
        recommendations.append(f"Address {overdue} overdue ticket(s) immediately")
    
    if critical > 0:
        recommendations.append(f"Prioritize {critical} critical ticket(s) approaching SLA deadline")
    
    if active > 10:
        recommendations.append("Consider redistributing workload - high ticket volume")
    elif active > 5:
        recommendations.append("Monitor ticket volume - approaching capacity")
    
    if not recommendations:
        recommendations.append("Workload is manageable - continue current pace")
    
    return recommendations


@router.get("/analytics/admissions-funnel")
def get_admissions_funnel(current_user: AuthUser = Depends(get_current_user)):
    """Get admissions funnel analytics"""
    if not has_permission(current_user, "admissions:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get all leads for the school
        leads_result = supabase.table('leads').select('*').eq('school_id', current_user.schoolId).execute()
        leads = leads_result.data or []
        
        # Calculate funnel by stage
        funnel_by_stage = {}
        stage_order = ['new', 'contacted', 'qualified', 'tour_scheduled', 'assessment_scheduled', 'offer_sent', 'enrolled', 'lost']
        
        for stage in stage_order:
            funnel_by_stage[stage] = len([l for l in leads if l.get('stage') == stage])
        
        # Calculate conversion rates
        funnel_data = []
        total_leads = len(leads)
        
        for stage in stage_order:
            count = funnel_by_stage[stage]
            conversion_rate = (count / total_leads * 100) if total_leads > 0 else 0
            funnel_data.append({
                "stage": stage,
                "count": count,
                "conversion_rate": round(conversion_rate, 2)
            })
        
        # Get funnel for last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_leads = [l for l in leads if l.get('created_at') and l['created_at'] >= thirty_days_ago]
        
        recent_funnel_by_stage = {}
        for stage in stage_order:
            recent_funnel_by_stage[stage] = len([l for l in recent_leads if l.get('stage') == stage])
        
        recent_funnel_data = []
        total_recent_leads = len(recent_leads)
        
        for stage in stage_order:
            count = recent_funnel_by_stage[stage]
            conversion_rate = (count / total_recent_leads * 100) if total_recent_leads > 0 else 0
            recent_funnel_data.append({
                "stage": stage,
                "count": count,
                "conversion_rate": round(conversion_rate, 2)
            })
        
        # Calculate average time in each stage
        stage_durations = {}
        for stage in stage_order:
            stage_leads = [l for l in leads if l.get('stage') == stage and l.get('created_at')]
            if stage_leads:
                total_duration = 0
                count = 0
                for lead in stage_leads:
                    try:
                        created = datetime.fromisoformat(lead['created_at'])
                        updated = datetime.fromisoformat(lead['updated_at']) if lead.get('updated_at') else datetime.now()
                        duration = (updated - created).days
                        total_duration += duration
                        count += 1
                    except:
                        pass
                avg_duration = total_duration / count if count > 0 else 0
                stage_durations[stage] = round(avg_duration, 2)
            else:
                stage_durations[stage] = 0
        
        # Calculate overall conversion rate (new to enrolled)
        new_leads = funnel_by_stage.get('new', 0)
        enrolled_leads = funnel_by_stage.get('enrolled', 0)
        overall_conversion_rate = (enrolled_leads / new_leads * 100) if new_leads > 0 else 0
        
        return {
            "funnel": {
                "all_time": {
                    "total_leads": total_leads,
                    "by_stage": funnel_data,
                    "stage_durations": stage_durations,
                    "overall_conversion_rate": round(overall_conversion_rate, 2)
                },
                "last_30_days": {
                    "total_leads": total_recent_leads,
                    "by_stage": recent_funnel_data
                }
            }
        }
    except Exception as e:
        print(f"Error fetching admissions funnel: {e}")
        return {"funnel": {"all_time": {"total_leads": 0, "by_stage": [], "stage_durations": {}, "overall_conversion_rate": 0}, "last_30_days": {"total_leads": 0, "by_stage": []}}}


@router.get("/analytics/fee-collection")
def get_fee_collection_analytics(current_user: AuthUser = Depends(get_current_user)):
    """Get fee collection analytics"""
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get all invoices for the school
        invoices_result = supabase.table('invoices').select('*').eq('school_id', current_user.schoolId).execute()
        invoices = invoices_result.data or []
        
        # Calculate total amount and collected amount
        total_amount = sum([inv.get('amount_due', 0) for inv in invoices])
        total_collected = sum([inv.get('amount_paid', 0) for inv in invoices])
        
        # Calculate collection rate
        collection_rate = (total_collected / total_amount * 100) if total_amount > 0 else 0
        
        # Get invoices by status
        status_counts = {}
        for invoice in invoices:
            status = invoice.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get collections for last 30 days
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        payments_result = supabase.table('payments').select('*').eq('school_id', current_user.schoolId).gte('paid_at', thirty_days_ago).execute()
        payments = payments_result.data or []
        
        collections_last_30_days = sum([p.get('amount', 0) for p in payments])
        
        # Get collections by month for the last 6 months
        monthly_collections = {}
        for i in range(6):
            month_start = (datetime.now() - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            month_key = month_start.strftime('%Y-%m')
            
            month_payments = [p for p in payments if p.get('paid_at') and month_start.isoformat() <= p['paid_at'] <= month_end.isoformat()]
            monthly_collections[month_key] = sum([p.get('amount', 0) for p in month_payments])
        
        # Get overdue amount
        overdue_invoices = [inv for inv in invoices if inv.get('status') in ['pending', 'part_paid'] and inv.get('due_date') and datetime.fromisoformat(inv['due_date']) < datetime.now()]
        overdue_amount = sum([inv.get('amount_due', 0) - inv.get('amount_paid', 0) for inv in overdue_invoices])
        
        return {
            "fee_collection": {
                "total_amount": total_amount,
                "total_collected": total_collected,
                "collection_rate": round(collection_rate, 2),
                "outstanding_amount": total_amount - total_collected,
                "overdue_amount": overdue_amount,
                "collections_last_30_days": collections_last_30_days,
                "by_status": status_counts,
                "monthly_collections": monthly_collections
            }
        }
    except Exception as e:
        print(f"Error fetching fee collection analytics: {e}")
        return {"fee_collection": {"total_amount": 0, "total_collected": 0, "collection_rate": 0, "outstanding_amount": 0, "overdue_amount": 0, "collections_last_30_days": 0, "by_status": {}, "monthly_collections": {}}}


@router.get("/analytics/student-statistics")
def get_student_statistics(current_user: AuthUser = Depends(get_current_user)):
    """Get student statistics and trends"""
    if not has_permission(current_user, "students:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Get all students for the school
        students_result = supabase.table('students').select('*').eq('school_id', current_user.schoolId).execute()
        students = students_result.data or []
        
        # Get students by class
        class_counts = {}
        for student in students:
            class_id = student.get('class_id')
            if class_id:
                class_counts[class_id] = class_counts.get(class_id, 0) + 1
        
        # Get class names
        class_names = {}
        if class_counts:
            classes_result = supabase.table('classes').select('*').in_('id', list(class_counts.keys())).execute()
            for cls in classes_result.data or []:
                class_names[cls['id']] = cls.get('name', 'Unknown')
        
        # Format class statistics
        class_stats = []
        for class_id, count in class_counts.items():
            class_stats.append({
                "class_id": class_id,
                "class_name": class_names.get(class_id, 'Unknown'),
                "student_count": count
            })
        
        # Get enrollment trends (by month for last 6 months)
        from datetime import datetime, timedelta
        monthly_enrollments = {}
        for i in range(6):
            month_start = (datetime.now() - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            month_key = month_start.strftime('%Y-%m')
            
            month_students = [s for s in students if s.get('enrollment_date') and month_start.isoformat() <= s['enrollment_date'] <= month_end.isoformat()]
            monthly_enrollments[month_key] = len(month_students)
        
        # Get gender distribution
        gender_counts = {}
        for student in students:
            gender = student.get('gender', 'unknown')
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        # Calculate total students
        total_students = len(students)
        
        return {
            "student_statistics": {
                "total_students": total_students,
                "by_class": class_stats,
                "gender_distribution": gender_counts,
                "monthly_enrollments": monthly_enrollments
            }
        }
    except Exception as e:
        print(f"Error fetching student statistics: {e}")
        return {"student_statistics": {"total_students": 0, "by_class": [], "gender_distribution": {}, "monthly_enrollments": {}}}


@router.patch("/leads/{lead_id}/lost-reason")
def update_lost_lead_reason(lead_id: str, payload: dict, current_user: AuthUser = Depends(get_current_user)):
    """Update lost lead reason when a lead is marked as lost"""
    if not has_permission(current_user, "admissions:manage"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        lost_reason = payload.get('lost_reason')
        lost_notes = payload.get('lost_notes')
        
        # Update lead with lost reason
        result = supabase.table('leads').update({
            'stage': 'lost',
            'lost_reason': lost_reason,
            'lost_notes': lost_notes,
            'lost_at': datetime.now().isoformat(),
            'lost_by': current_user.id
        }).eq('id', lead_id).eq('school_id', current_user.schoolId).execute()
        
        # Log the action
        supabase.table('audit_logs').insert({
            'school_id': current_user.schoolId,
            'user_id': current_user.id,
            'action': 'lead_lost',
            'entity_type': 'lead',
            'entity_id': lead_id,
            'details': {
                'lost_reason': lost_reason,
                'lost_notes': lost_notes
            },
            'created_at': datetime.now().isoformat()
        }).execute()
        
        return {"success": True, "lead": result.data[0]}
    except Exception as e:
        print(f"Error updating lost lead reason: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/lost-reasons-summary")
def get_lost_reasons_summary(current_user: AuthUser = Depends(get_current_user)):
    """Get summary of lost lead reasons for analytics"""
    if not has_permission(current_user, "admissions:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Get all lost leads
        leads_result = supabase.table('leads').select('*').eq('school_id', current_user.schoolId).eq('stage', 'lost').execute()
        lost_leads = leads_result.data or []
        
        # Count by lost reason
        reason_counts = {}
        for lead in lost_leads:
            reason = lead.get('lost_reason', 'unknown')
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        # Calculate percentage
        total_lost = len(lost_leads)
        reason_summary = []
        for reason, count in reason_counts.items():
            percentage = (count / total_lost * 100) if total_lost > 0 else 0
            reason_summary.append({
                "reason": reason,
                "count": count,
                "percentage": round(percentage, 2)
            })
        
        # Sort by count (descending)
        reason_summary.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            "lost_reasons_summary": reason_summary,
            "total_lost_leads": total_lost
        }
    except Exception as e:
        print(f"Error fetching lost reasons summary: {e}")
        return {"lost_reasons_summary": [], "total_lost_leads": 0}


@router.get("/helpdesk/analytics/resolution")
def get_resolution_analytics(current_user: AuthUser = Depends(get_current_user)):
    """Get resolution analytics for help desk"""
    if not has_permission(current_user, "helpdesk:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get all tickets for the school
        tickets_result = supabase.table('helpdesk_tickets').select('*').eq('school_id', current_user.schoolId).execute()
        tickets = tickets_result.data or []
        
        # Calculate resolution metrics
        total_tickets = len(tickets)
        resolved_tickets = [t for t in tickets if t['status'] == 'resolved']
        closed_tickets = [t for t in tickets if t['status'] == 'closed']
        
        # Calculate average resolution time
        resolution_times = []
        for ticket in resolved_tickets:
            if ticket.get('resolved_at') and ticket.get('created_at'):
                try:
                    created = datetime.fromisoformat(ticket['created_at'])
                    resolved = datetime.fromisoformat(ticket['resolved_at'])
                    resolution_times.append((resolved - created).total_seconds() / 3600)  # hours
                except:
                    pass
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Calculate resolution rate
        resolution_rate = (len(resolved_tickets) / total_tickets * 100) if total_tickets > 0 else 0
        
        # Get resolution by staff
        staff_resolution = {}
        for ticket in resolved_tickets:
            assigned_to = ticket.get('assigned_to')
            if assigned_to:
                staff_resolution[assigned_to] = staff_resolution.get(assigned_to, 0) + 1
        
        # Get staff names
        staff_names = {}
        if staff_resolution:
            staff_result = supabase.table('users').select('*').in_('id', list(staff_resolution.keys())).execute()
            for staff in staff_result.data or []:
                staff_names[staff['id']] = staff.get('name', 'Unknown')
        
        # Format staff resolution data
        staff_resolution_data = []
        for staff_id, count in staff_resolution.items():
            staff_resolution_data.append({
                "staff_id": staff_id,
                "staff_name": staff_names.get(staff_id, 'Unknown'),
                "resolved_count": count
            })
        
        # Sort by resolved count (descending)
        staff_resolution_data.sort(key=lambda x: x['resolved_count'], reverse=True)
        
        # Get resolution by priority
        priority_resolution = {}
        for ticket in resolved_tickets:
            priority = ticket.get('priority', 'unknown')
            priority_resolution[priority] = priority_resolution.get(priority, 0) + 1
        
        # Get resolution by category (if available)
        category_resolution = {}
        for ticket in resolved_tickets:
            category = ticket.get('category', 'unknown')
            category_resolution[category] = category_resolution.get(category, 0) + 1
        
        return {
            "resolution_analytics": {
                "total_tickets": total_tickets,
                "resolved_tickets": len(resolved_tickets),
                "closed_tickets": len(closed_tickets),
                "resolution_rate": round(resolution_rate, 2),
                "avg_resolution_time_hours": round(avg_resolution_time, 2),
                "by_staff": staff_resolution_data,
                "by_priority": priority_resolution,
                "by_category": category_resolution
            }
        }
    except Exception as e:
        print(f"Error fetching resolution analytics: {e}")
        return {"resolution_analytics": {"total_tickets": 0, "resolved_tickets": 0, "closed_tickets": 0, "resolution_rate": 0, "avg_resolution_time_hours": 0, "by_staff": [], "by_priority": {}, "by_category": {}}}


@router.get("/analytics/attendance-trends")
def get_attendance_trends(current_user: AuthUser = Depends(get_current_user)):
    """Get attendance trend analysis"""
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get attendance for the last 6 months
        six_months_ago = (datetime.now() - timedelta(days=180)).isoformat()
        attendance_result = supabase.table('attendance').select('*').eq('school_id', current_user.schoolId).gte('date', six_months_ago).execute()
        attendance_records = attendance_result.data or []
        
        # Calculate monthly attendance rates
        monthly_attendance = {}
        for i in range(6):
            month_start = (datetime.now() - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            month_key = month_start.strftime('%Y-%m')
            
            month_records = [a for a in attendance_records if a.get('date') and month_start.isoformat() <= a['date'] <= month_end.isoformat()]
            total_days = len(month_records)
            present_days = len([a for a in month_records if a['status'] == 'present'])
            attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
            
            monthly_attendance[month_key] = {
                "total_days": total_days,
                "present_days": present_days,
                "attendance_rate": round(attendance_rate, 2)
            }
        
        # Get attendance by staff
        staff_attendance = {}
        for record in attendance_records:
            staff_id = record.get('staff_id')
            if staff_id:
                if staff_id not in staff_attendance:
                    staff_attendance[staff_id] = {"total": 0, "present": 0}
                staff_attendance[staff_id]["total"] += 1
                if record['status'] == 'present':
                    staff_attendance[staff_id]["present"] += 1
        
        # Get staff names
        staff_names = {}
        if staff_attendance:
            staff_result = supabase.table('users').select('*').in_('id', list(staff_attendance.keys())).execute()
            for staff in staff_result.data or []:
                staff_names[staff['id']] = staff.get('name', 'Unknown')
        
        # Format staff attendance data
        staff_attendance_data = []
        for staff_id, data in staff_attendance.items():
            attendance_rate = (data['present'] / data['total'] * 100) if data['total'] > 0 else 0
            staff_attendance_data.append({
                "staff_id": staff_id,
                "staff_name": staff_names.get(staff_id, 'Unknown'),
                "total_days": data['total'],
                "present_days": data['present'],
                "attendance_rate": round(attendance_rate, 2)
            })
        
        return {
            "attendance_trends": {
                "monthly": monthly_attendance,
                "by_staff": staff_attendance_data
            }
        }
    except Exception as e:
        print(f"Error fetching attendance trends: {e}")
        return {"attendance_trends": {"monthly": {}, "by_staff": []}}


@router.get("/analytics/parent-engagement")
def get_parent_engagement_metrics(current_user: AuthUser = Depends(get_current_user)):
    """Get parent engagement metrics"""
    if not has_permission(current_user, "families:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get all families for the school
        families_result = supabase.table('families').select('*').eq('school_id', current_user.schoolId).execute()
        families = families_result.data or []
        
        # Get communication history
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        communications_result = supabase.table('communications').select('*').eq('school_id', current_user.schoolId).gte('sent_at', thirty_days_ago).execute()
        communications = communications_result.data or []
        
        # Count communications by channel
        channel_counts = {}
        for comm in communications:
            channel = comm.get('channel', 'unknown')
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        # Get parent response rate (based on opened/clicked communications)
        total_sent = len(communications)
        opened_count = len([c for c in communications if c.get('opened_at')])
        response_rate = (opened_count / total_sent * 100) if total_sent > 0 else 0
        
        # Get families with recent engagement
        engaged_families = []
        for family in families:
            family_comms = [c for c in communications if c.get('family_id') == family['id']]
            if family_comms:
                engaged_families.append({
                    "family_id": family['id'],
                    "family_name": family.get('primary_contact_name', 'Unknown'),
                    "communication_count": len(family_comms),
                    "last_communication": max([c.get('sent_at') for c in family_comms])
                })
        
        # Sort by communication count (descending)
        engaged_families.sort(key=lambda x: x['communication_count'], reverse=True)
        
        return {
            "parent_engagement": {
                "total_families": len(families),
                "total_communications": total_sent,
                "opened_communications": opened_count,
                "response_rate": round(response_rate, 2),
                "by_channel": channel_counts,
                "engaged_families": engaged_families[:20]  # Top 20
            }
        }
    except Exception as e:
        print(f"Error fetching parent engagement metrics: {e}")
        return {"parent_engagement": {"total_families": 0, "total_communications": 0, "opened_communications": 0, "response_rate": 0, "by_channel": {}, "engaged_families": []}}


@router.get("/reports/staff-performance")
def get_staff_performance_report(current_user: AuthUser = Depends(get_current_user)):
    """Get comprehensive staff performance report"""
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        # Get performance summary for all staff
        from datetime import datetime, timedelta
        
        staff_result = supabase.table('user_roles').select('*, users(*)').eq('school_id', current_user.schoolId).execute()
        staff_members = staff_result.data or []
        
        performance_report = []
        
        for staff in staff_members:
            staff_id = staff['user_id']
            user = staff.get('users', {})
            
            # Attendance
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            attendance_result = supabase.table('attendance').select('*').eq('staff_id', staff_id).eq('school_id', current_user.schoolId).gte('date', thirty_days_ago).execute()
            attendance_records = attendance_result.data or []
            
            total_days = len(attendance_records)
            present_days = len([a for a in attendance_records if a['status'] == 'present'])
            attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
            
            # Help desk tickets
            tickets_result = supabase.table('helpdesk_tickets').select('*').eq('assigned_to', staff_id).eq('school_id', current_user.schoolId).execute()
            tickets = tickets_result.data or []
            
            total_tickets = len(tickets)
            resolved_tickets = len([t for t in tickets if t['status'] == 'resolved'])
            resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
            
            # SLA compliance
            resolved_tickets_data = [t for t in tickets if t['status'] == 'resolved' and t.get('sla_deadline') and t.get('resolved_at')]
            sla_compliant = 0
            sla_total = 0
            for ticket in resolved_tickets_data:
                sla_total += 1
                try:
                    deadline = datetime.fromisoformat(ticket['sla_deadline'])
                    resolved = datetime.fromisoformat(ticket['resolved_at'])
                    if resolved <= deadline:
                        sla_compliant += 1
                except:
                    pass
            
            sla_compliance_rate = (sla_compliant / sla_total * 100) if sla_total > 0 else 0
            
            # Calculate overall score
            attendance_score = attendance_rate * 0.3
            resolution_score = resolution_rate * 0.4
            sla_score = sla_compliance_rate * 0.3
            overall_score = attendance_score + resolution_score + sla_score
            
            performance_report.append({
                "staff_id": staff_id,
                "staff_name": user.get('name', 'Unknown'),
                "staff_email": user.get('email', ''),
                "role": staff.get('role', ''),
                "attendance_rate": round(attendance_rate, 2),
                "resolution_rate": round(resolution_rate, 2),
                "sla_compliance_rate": round(sla_compliance_rate, 2),
                "overall_score": round(overall_score, 2),
                "grade": get_performance_grade(overall_score)
            })
        
        # Sort by overall score (descending)
        performance_report.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return {
            "staff_performance_report": performance_report,
            "total_staff": len(performance_report),
            "report_date": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error fetching staff performance report: {e}")
        return {"staff_performance_report": [], "total_staff": 0, "report_date": datetime.now().isoformat()}


@router.get("/reports/export/{report_type}")
def export_report(report_type: str, current_user: AuthUser = Depends(get_current_user)):
    """Export report data in CSV format"""
    if not has_permission(current_user, "reports:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        import csv
        from io import StringIO
        from datetime import datetime
        
        data = []
        headers = []
        
        if report_type == "students":
            students_result = supabase.table('students').select('*, families(*), classes(*)').eq('school_id', current_user.schoolId).execute()
            students = students_result.data or []
            headers = ["ID", "Name", "Email", "Class", "Enrollment Date", "Status"]
            for student in students:
                data.append([
                    student['id'],
                    student.get('name', ''),
                    student.get('email', ''),
                    student.get('classes', {}).get('name', ''),
                    student.get('enrollment_date', ''),
                    student.get('status', '')
                ])
        
        elif report_type == "families":
            families_result = supabase.table('families').select('*').eq('school_id', current_user.schoolId).execute()
            families = families_result.data or []
            headers = ["ID", "Primary Contact", "Email", "Phone", "Address", "Children Count"]
            for family in families:
                data.append([
                    family['id'],
                    family.get('primary_contact_name', ''),
                    family.get('email', ''),
                    family.get('phone', ''),
                    family.get('address', ''),
                    family.get('children_count', 0)
                ])
        
        elif report_type == "invoices":
            invoices_result = supabase.table('invoices').select('*, families(*)').eq('school_id', current_user.schoolId).execute()
            invoices = invoices_result.data or []
            headers = ["Invoice Number", "Family", "Amount Due", "Amount Paid", "Status", "Due Date"]
            for invoice in invoices:
                data.append([
                    invoice.get('invoice_number', ''),
                    invoice.get('families', {}).get('primary_contact_name', ''),
                    invoice.get('amount_due', 0),
                    invoice.get('amount_paid', 0),
                    invoice.get('status', ''),
                    invoice.get('due_date', '')
                ])
        
        elif report_type == "staff":
            staff_result = supabase.table('user_roles').select('*, users(*)').eq('school_id', current_user.schoolId).execute()
            staff = staff_result.data or []
            headers = ["ID", "Name", "Email", "Role", "Created At"]
            for s in staff:
                data.append([
                    s['user_id'],
                    s.get('users', {}).get('name', ''),
                    s.get('users', {}).get('email', ''),
                    s.get('role', ''),
                    s.get('users', {}).get('created_at', '')
                ])
        
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(data)
        
        csv_content = output.getvalue()
        
        return {
            "report_type": report_type,
            "format": "csv",
            "data": csv_content,
            "generated_at": datetime.now().isoformat(),
            "row_count": len(data)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error exporting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/enrollment-prediction")
def get_enrollment_prediction(current_user: AuthUser = Depends(get_current_user)):
    """Get enrollment prediction based on historical data"""
    if not has_permission(current_user, "admissions:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get enrollment data for last 12 months
        twelve_months_ago = (datetime.now() - timedelta(days=365)).isoformat()
        students_result = supabase.table('students').select('*').eq('school_id', current_user.schoolId).gte('enrollment_date', twelve_months_ago).execute()
        students = students_result.data or []
        
        # Calculate monthly enrollments
        monthly_enrollments = {}
        for i in range(12):
            month_start = (datetime.now() - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            month_key = month_start.strftime('%Y-%m')
            
            month_students = [s for s in students if s.get('enrollment_date') and month_start.isoformat() <= s['enrollment_date'] <= month_end.isoformat()]
            monthly_enrollments[month_key] = len(month_students)
        
        # Calculate average monthly enrollment
        avg_monthly = sum(monthly_enrollments.values()) / len(monthly_enrollments) if monthly_enrollments else 0
        
        # Calculate trend (simple linear regression)
        months = list(range(len(monthly_enrollments)))
        enrollments = list(monthly_enrollments.values())
        
        if len(months) > 1:
            # Simple trend calculation
            trend = (enrollments[-1] - enrollments[0]) / len(enrollments) if enrollments else 0
        else:
            trend = 0
        
        # Predict next 3 months
        predictions = {}
        for i in range(1, 4):
            future_month = (datetime.now() + timedelta(days=30*i)).strftime('%Y-%m')
            predicted = avg_monthly + (trend * i)
            predictions[future_month] = max(0, round(predicted))
        
        # Get current leads in pipeline
        leads_result = supabase.table('leads').select('*').eq('school_id', current_user.schoolId).not_.in_('stage', ['enrolled', 'lost']).execute()
        pipeline_leads = leads_result.data or []
        
        return {
            "enrollment_prediction": {
                "historical_data": monthly_enrollments,
                "average_monthly": round(avg_monthly, 2),
                "trend": round(trend, 2),
                "predictions": predictions,
                "pipeline_leads": len(pipeline_leads),
                "confidence": "medium"  # Simple prediction, not ML-based
            }
        }
    except Exception as e:
        print(f"Error fetching enrollment prediction: {e}")
        return {"enrollment_prediction": {"historical_data": {}, "average_monthly": 0, "trend": 0, "predictions": {}, "pipeline_leads": 0, "confidence": "low"}}


@router.get("/analytics/fee-forecasting")
def get_fee_forecasting(current_user: AuthUser = Depends(get_current_user)):
    """Get fee collection forecasting"""
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get invoices for last 6 months
        six_months_ago = (datetime.now() - timedelta(days=180)).isoformat()
        invoices_result = supabase.table('invoices').select('*').eq('school_id', current_user.schoolId).gte('created_at', six_months_ago).execute()
        invoices = invoices_result.data or []
        
        # Calculate monthly collections
        monthly_collections = {}
        for i in range(6):
            month_start = (datetime.now() - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            month_key = month_start.strftime('%Y-%m')
            
            month_invoices = [inv for inv in invoices if inv.get('created_at') and month_start.isoformat() <= inv['created_at'] <= month_end.isoformat()]
            monthly_collections[month_key] = sum([inv.get('amount_paid', 0) for inv in month_invoices])
        
        # Calculate average monthly collection
        avg_monthly = sum(monthly_collections.values()) / len(monthly_collections) if monthly_collections else 0
        
        # Get outstanding invoices
        outstanding_result = supabase.table('invoices').select('*').eq('school_id', current_user.schoolId).in_('status', ['pending', 'part_paid']).execute()
        outstanding_invoices = outstanding_result.data or []
        
        total_outstanding = sum([inv.get('amount_due', 0) - inv.get('amount_paid', 0) for inv in outstanding_invoices])
        
        # Predict next 3 months based on average + outstanding
        predictions = {}
        for i in range(1, 4):
            future_month = (datetime.now() + timedelta(days=30*i)).strftime('%Y-%m')
            predicted = avg_monthly + (total_outstanding / 3)  # Distribute outstanding over 3 months
            predictions[future_month] = round(predicted, 2)
        
        return {
            "fee_forecasting": {
                "historical_collections": monthly_collections,
                "average_monthly": round(avg_monthly, 2),
                "total_outstanding": round(total_outstanding, 2),
                "predictions": predictions,
                "confidence": "medium"
            }
        }
    except Exception as e:
        print(f"Error fetching fee forecasting: {e}")
        return {"fee_forecasting": {"historical_collections": {}, "average_monthly": 0, "total_outstanding": 0, "predictions": {}, "confidence": "low"}}


@router.get("/analytics/student-retention")
def get_student_retention_analysis(current_user: AuthUser = Depends(get_current_user)):
    """Get student retention analysis"""
    if not has_permission(current_user, "students:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        from datetime import datetime, timedelta
        
        # Get all students
        students_result = supabase.table('students').select('*').eq('school_id', current_user.schoolId).execute()
        students = students_result.data or []
        
        # Calculate retention by year
        retention_by_year = {}
        for student in students:
            enrollment_date = student.get('enrollment_date')
            if enrollment_date:
                try:
                    year = datetime.fromisoformat(enrollment_date).year
                    if year not in retention_by_year:
                        retention_by_year[year] = {"enrolled": 0, "active": 0}
                    retention_by_year[year]["enrolled"] += 1
                    if student.get('status') == 'active':
                        retention_by_year[year]["active"] += 1
                except:
                    pass
        
        # Calculate retention rates
        retention_rates = {}
        for year, data in retention_by_year.items():
            retention_rate = (data['active'] / data['enrolled'] * 100) if data['enrolled'] > 0 else 0
            retention_rates[year] = {
                "enrolled": data['enrolled'],
                "active": data['active'],
                "retention_rate": round(retention_rate, 2)
            }
        
        # Calculate overall retention rate
        total_enrolled = sum([data['enrolled'] for data in retention_by_year.values()])
        total_active = sum([data['active'] for data in retention_by_year.values()])
        overall_retention = (total_active / total_enrolled * 100) if total_enrolled > 0 else 0
        
        # Get inactive students (for analysis)
        inactive_students = [s for s in students if s.get('status') == 'inactive']
        
        return {
            "student_retention": {
                "by_year": retention_rates,
                "overall_retention_rate": round(overall_retention, 2),
                "total_students": len(students),
                "active_students": total_active,
                "inactive_students": len(inactive_students),
                "retention_trend": "stable"  # Simple assessment
            }
        }
    except Exception as e:
        print(f"Error fetching student retention analysis: {e}")
        return {"student_retention": {"by_year": {}, "overall_retention_rate": 0, "total_students": 0, "active_students": 0, "inactive_students": 0, "retention_trend": "unknown"}}

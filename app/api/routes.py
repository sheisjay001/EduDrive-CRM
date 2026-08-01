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

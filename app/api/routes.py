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

        # Create user in Supabase Auth
        response = supabase.auth.sign_up({
            "email": payload["email"],
            "password": payload["password"],
            "options": {
                "data": {
                    "full_name": payload["fullName"]
                }
            }
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
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
    return {"message": f"If an account exists for {payload.email}, a reset link has been sent."}


@router.post("/auth/reset-password")
def reset_password(payload: ResetPasswordRequest) -> dict[str, str]:
    return {"message": "Password has been successfully updated. Please sign in with your new password."}


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
        result = supabase.table('leads').insert({
            'school_id': current_user.schoolId,
            'first_name': payload.firstName,
            'last_name': payload.lastName,
            'parent_name': payload.parentName,
            'parent_phone': payload.parentPhone,
            'parent_email': payload.parentEmail,
            'source': payload.source,
            'stage': 'new',
            'interested_class': payload.interestedClass
        }).execute()
        return demo_data.get_lead_detail(str(result.data[0]['id']))
    except Exception as e:
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
    return demo_data.convert_lead(lead_id, payload)


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


@router.get("/finance/fee-structures", response_model=FeeStructuresResponse)
def fee_structures(current_user: AuthUser = Depends(get_current_user)) -> FeeStructuresResponse:
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    supabase = get_supabase_client()
    try:
        result = supabase.table('fee_structures').select('*').eq('school_id', current_user.schoolId).execute()
        return demo_data.get_fee_structures()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        result = supabase.table('message_templates').select('*').eq('school_id', current_user.schoolId).execute()
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
        raise HTTPException(status_code=500, detail=str(e))


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
        result = supabase.table('users').select('*').eq('school_id', current_user.schoolId).execute()
        return demo_data.get_staff()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        
        result = supabase.table('schools').update(update_data).eq('id', current_user.schoolId).execute()
        return {"success": True, "school": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import (
    authenticate_user,
    create_tokens_for_user,
    decode_refresh_token,
    get_current_user,
    require_any_role,
    has_permission,
    get_db,
)
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

router = APIRouter()


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = authenticate_user(db, payload.email, payload.password)
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
def create_lead(payload: LeadCreateRequest, db: Session = Depends(get_db), current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> LeadDetailResponse:
    from app.repositories import LeadRepository
    lead_repo = LeadRepository(db)
    
    lead = lead_repo.create(
        school_id=current_user.schoolId,
        first_name=payload.firstName,
        last_name=payload.lastName,
        parent_name=payload.parentName,
        parent_phone=payload.parentPhone,
        parent_email=payload.parentEmail,
        source=payload.source,
        stage=payload.stage,
        interested_class=payload.interestedClass,
        follow_up_at=datetime.fromisoformat(payload.followUpAt) if payload.followUpAt else None,
        notes="",
        status="active"
    )
    
    return LeadDetailResponse(
        id=lead.id,
        childName=f"{lead.first_name} {lead.last_name}",
        parentName=lead.parent_name,
        parentEmail=lead.parent_email,
        parentPhone=lead.parent_phone,
        source=lead.source,
        stage=lead.stage,
        classInterest=lead.interested_class or "",
        followUp=lead.follow_up_at.strftime("%Y-%m-%d") if lead.follow_up_at else "Not scheduled",
        notes=lead.notes,
        createdAt=lead.created_at.strftime("%Y-%m-%d")
    )


@router.patch("/leads/{lead_id}", response_model=LeadDetailResponse)
def update_lead(lead_id: str, payload: LeadUpdateRequest, db: Session = Depends(get_db), current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> LeadDetailResponse:
    from app.repositories import LeadRepository
    lead_repo = LeadRepository(db)
    
    lead = lead_repo.get_by_id(lead_id)
    if not lead or lead.school_id != current_user.schoolId:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = {}
    if payload.stage:
        update_data["stage"] = payload.stage
    if payload.interestedClass is not None:
        update_data["interested_class"] = payload.interestedClass
    if payload.followUpAt is not None:
        update_data["follow_up_at"] = datetime.fromisoformat(payload.followUpAt) if payload.followUpAt else None
    if payload.notes is not None:
        update_data["notes"] = payload.notes
    
    lead_repo.update(lead, **update_data)
    
    return LeadDetailResponse(
        id=lead.id,
        childName=f"{lead.first_name} {lead.last_name}",
        parentName=lead.parent_name,
        parentEmail=lead.parent_email,
        parentPhone=lead.parent_phone,
        source=lead.source,
        stage=lead.stage,
        classInterest=lead.interested_class or "",
        followUp=lead.follow_up_at.strftime("%Y-%m-%d") if lead.follow_up_at else "Not scheduled",
        notes=lead.notes,
        createdAt=lead.created_at.strftime("%Y-%m-%d")
    )


@router.patch("/leads/{lead_id}/stage")
def update_lead_stage(lead_id: str, payload: dict, db: Session = Depends(get_db), current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict:
    from app.repositories import LeadRepository
    lead_repo = LeadRepository(db)
    
    lead = lead_repo.get_by_id(lead_id)
    if not lead or lead.school_id != current_user.schoolId:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead_repo.update(lead, stage=payload.get("stage", lead.stage))
    
    return {"id": lead.id, "stage": lead.stage}


@router.get("/families", response_model=FamiliesResponse)
def families(current_user: AuthUser = Depends(get_current_user)) -> FamiliesResponse:
    if not has_permission(current_user, "families:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_families()


@router.get("/families/{family_id}", response_model=FamilyDetailResponse)
def family_detail(family_id: str, current_user: AuthUser = Depends(get_current_user)) -> FamilyDetailResponse:
    if not has_permission(current_user, "families:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_family_detail(family_id)


@router.get("/parents", response_model=ParentsResponse)
def parents(current_user: AuthUser = Depends(get_current_user)) -> ParentsResponse:
    if not has_permission(current_user, "parents:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_parents()


@router.get("/parents/{parent_id}", response_model=ParentDetailResponse)
def parent_detail(parent_id: str, current_user: AuthUser = Depends(get_current_user)) -> ParentDetailResponse:
    if not has_permission(current_user, "parents:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_parent_detail(parent_id)


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
    return demo_data.get_student_detail(student_id)


@router.get("/finance/overview", response_model=FinanceResponse)
def finance(current_user: AuthUser = Depends(get_current_user)) -> FinanceResponse:
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_finance()


@router.get("/finance/fee-structures", response_model=FeeStructuresResponse)
def fee_structures(current_user: AuthUser = Depends(get_current_user)) -> FeeStructuresResponse:
    if not has_permission(current_user, "finance:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return demo_data.get_fee_structures()


@router.post("/invoices", response_model=InvoiceDetailResponse)
def create_invoice(payload: InvoiceCreateRequest, current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> InvoiceDetailResponse:
    return demo_data.create_invoice(payload, current_user.schoolId)


@router.post("/payments", response_model=PaymentRecord)
def record_payment(payload: PaymentRecord, current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> PaymentRecord:
    return demo_data.record_payment(payload)


@router.post("/payments/paystack/initialize", response_model=PaystackInitResponse)
def init_paystack(current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> PaystackInitResponse:
    return demo_data.init_paystack()


@router.post("/payments/flutterwave/initialize", response_model=FlutterwaveInitResponse)
def init_flutterwave(current_user: AuthUser = Depends(require_any_role(["school_admin", "bursar"]))) -> FlutterwaveInitResponse:
    return demo_data.init_flutterwave()


@router.post("/webhooks/paystack")
def webhook_paystack(payload: dict, db: Session = Depends(get_db)) -> dict[str, str]:
    from app.repositories import PaymentRepository, InvoiceRepository
    payment_repo = PaymentRepository(db)
    invoice_repo = InvoiceRepository(db)
    
    # Handle Paystack webhook for payment confirmation
    event = payload.get("event")
    data = payload.get("data", {})
    
    if event == "charge.success":
        reference = data.get("reference")
        amount = data.get("amount") / 100  # Convert from kobo to naira
        
        # Find payment by reference
        payments = payment_repo.get_by_provider_reference(reference)
        if payments:
            payment = payments[0]
            # Update payment status
            payment_repo.update(payment, paid_at=datetime.now())
            
            # Update invoice
            invoice = invoice_repo.get_by_id(payment.invoice_id)
            if invoice:
                invoice_repo.update(invoice, amount_paid=invoice.amount_paid + amount, status="paid" if invoice.amount_paid + amount >= invoice.amount_due else "partial")
    
    return {"status": "success"}


@router.post("/webhooks/flutterwave")
def webhook_flutterwave(payload: dict, db: Session = Depends(get_db)) -> dict[str, str]:
    from app.repositories import PaymentRepository, InvoiceRepository
    payment_repo = PaymentRepository(db)
    invoice_repo = InvoiceRepository(db)
    
    # Handle Flutterwave webhook for payment confirmation
    event = payload.get("event")
    data = payload.get("data", {})
    
    if event == "charge.completed":
        reference = data.get("tx_ref")
        amount = data.get("amount")
        
        # Find payment by reference
        payments = payment_repo.get_by_provider_reference(reference)
        if payments:
            payment = payments[0]
            # Update payment status
            payment_repo.update(payment, paid_at=datetime.now())
            
            # Update invoice
            invoice = invoice_repo.get_by_id(payment.invoice_id)
            if invoice:
                invoice_repo.update(invoice, amount_paid=invoice.amount_paid + amount, status="paid" if invoice.amount_paid + amount >= invoice.amount_due else "partial")
    
    return {"status": "success"}


@router.post("/payments/initialize")
def initialize_payment(payload: dict, db: Session = Depends(get_db), current_user: AuthUser = Depends(get_current_user)) -> dict:
    from app.repositories import InvoiceRepository, PaymentRepository
    invoice_repo = InvoiceRepository(db)
    payment_repo = PaymentRepository(db)
    
    invoice_id = payload.get("invoice_id")
    provider = payload.get("provider", "paystack")  # paystack or flutterwave
    
    invoice = invoice_repo.get_by_id(invoice_id)
    if not invoice or invoice.school_id != current_user.schoolId:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Create payment record
    payment = payment_repo.create(
        school_id=current_user.schoolId,
        invoice_id=invoice_id,
        amount=invoice.amount_due - invoice.amount_paid,
        method=provider,
        provider_reference="",
    )
    
    # Return payment initialization response
    if provider == "paystack":
        return {
            "payment_id": payment.id,
            "authorization_url": f"https://paystack.co/pay/{payment.id}",
            "reference": payment.id,
            "amount": invoice.amount_due - invoice.amount_paid,
        }
    else:
        return {
            "payment_id": payment.id,
            "authorization_url": f"https://flutterwave.com/pay/{payment.id}",
            "reference": payment.id,
            "amount": invoice.amount_due - invoice.amount_paid,
        }


@router.get("/messages/overview", response_model=MessagingResponse)
def messaging(db: Session = Depends(get_db), current_user: AuthUser = Depends(get_current_user)) -> MessagingResponse:
    if not has_permission(current_user, "messaging:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    from app.repositories import MessageLogRepository
    message_repo = MessageLogRepository(db)
    
    messages = message_repo.get_by_school(current_user.schoolId)
    
    # Calculate metrics
    email_sent = len([m for m in messages if m.channel == "email"])
    sms_sent = len([m for m in messages if m.channel == "sms"])
    whatsapp_sent = len([m for m in messages if m.channel == "whatsapp"])
    
    total = len(messages)
    email_rate = f"{int((email_sent / total * 100) if total > 0 else 0)}%"
    sms_rate = f"{int((sms_sent / total * 100) if total > 0 else 0)}%"
    whatsapp_rate = f"{int((whatsapp_sent / total * 100) if total > 0 else 0)}%"
    
    return MessagingResponse(
        metrics=[
            {"channel": "Email", "sent": str(email_sent), "openRate": email_rate, "delivery": "98%"},
            {"channel": "SMS", "sent": str(sms_sent), "openRate": sms_rate, "delivery": "95%"},
            {"channel": "WhatsApp", "sent": str(whatsapp_sent), "openRate": whatsapp_rate, "delivery": "92%"},
        ],
        campaigns=[
            {
                "title": "Term Fee Reminder",
                "audience": "All Parents",
                "channel": "Email",
                "status": "Completed",
                "sentAt": "2026-07-28",
            },
            {
                "title": "Mid-Term Assessment Notice",
                "audience": "SS 1-3 Students",
                "channel": "SMS",
                "status": "Scheduled",
                "sentAt": "2026-08-05",
            },
        ]
    )


@router.get("/messages/templates", response_model=MessageTemplatesResponse)
def message_templates(current_user: AuthUser = Depends(get_current_user)) -> MessageTemplatesResponse:
    if not has_permission(current_user, "messaging:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    return MessageTemplatesResponse(
        templates=[
            {"id": "1", "name": "Welcome Email", "channel": "email", "useCase": "Onboarding", "lastEdited": "2026-07-20"},
            {"id": "2", "name": "Fee Reminder", "channel": "sms", "useCase": "Collections", "lastEdited": "2026-07-15"},
            {"id": "3", "name": "Payment Receipt", "channel": "email", "useCase": "Finance", "lastEdited": "2026-07-18"},
            {"id": "4", "name": "Assessment Notice", "channel": "whatsapp", "useCase": "Academic", "lastEdited": "2026-07-22"},
            {"id": "5", "name": "Complaint Response", "channel": "email", "useCase": "Support", "lastEdited": "2026-07-25"},
        ]
    )


@router.post("/messages/broadcast")
def broadcast_message(payload: BroadcastRequest, current_user: AuthUser = Depends(require_any_role(["school_admin", "admissions_officer"]))) -> dict[str, str]:
    return demo_data.broadcast_message(payload)


@router.get("/tickets", response_model=HelpdeskResponse)
def tickets(db: Session = Depends(get_db), current_user: AuthUser = Depends(get_current_user)) -> HelpdeskResponse:
    if not has_permission(current_user, "tickets:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    from app.repositories import TicketRepository
    ticket_repo = TicketRepository(db)
    
    tickets = ticket_repo.get_by_school(current_user.schoolId)
    
    return HelpdeskResponse(
        tickets=[
            {
                "id": ticket.id,
                "subject": ticket.subject,
                "parent": f"Parent of {ticket.family_id[:8]}",
                "priority": ticket.priority,
                "assignee": "Unassigned" if not ticket.assignee_user_id else "Staff",
                "sla": ticket.sla_due_at.strftime("%Y-%m-%d") if ticket.sla_due_at else "Not set",
                "status": ticket.status,
            }
            for ticket in tickets
        ]
    )


@router.get("/tickets/{ticket_id}", response_model=TicketDetailResponse)
def ticket_detail(ticket_id: str, db: Session = Depends(get_db), current_user: AuthUser = Depends(get_current_user)) -> TicketDetailResponse:
    if not has_permission(current_user, "tickets:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    from app.repositories import TicketRepository
    ticket_repo = TicketRepository(db)
    
    ticket = ticket_repo.get_by_id(ticket_id)
    if not ticket or ticket.school_id != current_user.schoolId:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return TicketDetailResponse(
        id=ticket.id,
        subject=ticket.subject,
        parent=f"Parent of {ticket.family_id[:8]}",
        priority=ticket.priority,
        assignee="Unassigned" if not ticket.assignee_user_id else "Staff",
        sla=ticket.sla_due_at.strftime("%Y-%m-%d") if ticket.sla_due_at else "Not set",
        status=ticket.status,
        description=ticket.description,
        createdAt=ticket.created_at.strftime("%Y-%m-%d"),
        timeline=[{"time": ticket.created_at.strftime("%H:%M"), "note": "Ticket created"}]
    )


@router.post("/tickets")
def create_ticket(payload: dict, db: Session = Depends(get_db), current_user: AuthUser = Depends(get_current_user)) -> dict:
    from app.repositories import TicketRepository
    ticket_repo = TicketRepository(db)
    
    ticket = ticket_repo.create(
        school_id=current_user.schoolId,
        family_id=payload.get("familyId", ""),
        parent_id=payload.get("parentId", ""),
        subject=payload.get("subject", ""),
        priority=payload.get("priority", "Medium"),
        status="open",
        description=payload.get("description", ""),
    )
    
    return {"id": ticket.id}


@router.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: str, payload: dict, db: Session = Depends(get_db), current_user: AuthUser = Depends(require_any_role(["school_admin", "helpdesk_officer"]))) -> dict:
    from app.repositories import TicketRepository
    ticket_repo = TicketRepository(db)
    
    ticket = ticket_repo.get_by_id(ticket_id)
    if not ticket or ticket.school_id != current_user.schoolId:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    update_data = {}
    if payload.get("status"):
        update_data["status"] = payload["status"]
    if payload.get("assignee_user_id"):
        update_data["assignee_user_id"] = payload["assignee_user_id"]
    if payload.get("priority"):
        update_data["priority"] = payload["priority"]
    
    ticket_repo.update(ticket, **update_data)
    
    return {"id": ticket.id, "status": ticket.status}


@router.get("/invoices/{invoice_id}", response_model=InvoiceDetailResponse)
def invoice_detail(invoice_id: str, current_user: AuthUser = Depends(get_current_user)) -> InvoiceDetailResponse:
    return demo_data.get_invoice_detail(invoice_id)


@router.get("/staff/overview", response_model=StaffResponse)
def staff(db: Session = Depends(get_db), current_user: AuthUser = Depends(get_current_user)) -> StaffResponse:
    if not has_permission(current_user, "staff:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    from app.repositories import UserRepository
    user_repo = UserRepository(db)
    
    users = user_repo.get_by_school(current_user.schoolId)
    
    return StaffResponse(
        metrics=[
            {"label": "Total Staff", "value": str(len(users)), "note": "Active accounts"},
            {"label": "On Duty Today", "value": str(len(users)), "note": "Based on schedule"},
            {"label": "Avg Response", "value": "2.4h", "note": "Ticket resolution time"},
        ],
        people=[
            {
                "name": user.full_name,
                "role": "Staff",
                "attendance": "95%",
                "responseTime": "1.2h",
                "performance": "Strong",
            }
            for user in users
        ]
    )


@router.get("/reports/overview", response_model=ReportsResponse)
def reports(db: Session = Depends(get_db), current_user: AuthUser = Depends(get_current_user)) -> ReportsResponse:
    if not has_permission(current_user, "reports:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    from app.repositories import LeadRepository, InvoiceRepository, StudentRepository
    lead_repo = LeadRepository(db)
    invoice_repo = InvoiceRepository(db)
    student_repo = StudentRepository(db)
    
    leads = lead_repo.get_by_school(current_user.schoolId)
    invoices = invoice_repo.get_by_school(current_user.schoolId)
    students = student_repo.get_by_school(current_user.schoolId)
    
    enrolled_count = len([l for l in leads if l.stage == "enrolled"])
    total_collected = sum([inv.amount_paid or 0 for inv in invoices])
    total_due = sum([inv.amount_due for inv in invoices])
    
    return ReportsResponse(
        cards=[
            {"title": "Conversion Rate", "value": f"{int((enrolled_count / len(leads) * 100) if leads else 0)}%", "insight": "Admissions to enrollment"},
            {"title": "Collections", "value": f"₦{total_collected:,.0f}", "insight": "Total fees collected this term"},
            {"title": "Outstanding", "value": f"₦{total_due - total_collected:,.0f}", "insight": "Balance due across all invoices"},
        ],
        admissionsTrend=[
            {"label": "Jan", "value": 12},
            {"label": "Feb", "value": 18},
            {"label": "Mar", "value": 25},
            {"label": "Apr", "value": 32},
            {"label": "May", "value": 28},
            {"label": "Jun", "value": 35},
        ],
        collectionsTrend=[
            {"label": "Week 1", "value": 450000},
            {"label": "Week 2", "value": 520000},
            {"label": "Week 3", "value": 480000},
            {"label": "Week 4", "value": 610000},
        ]
    )


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
def settings(db: Session = Depends(get_db), current_user: AuthUser = Depends(get_current_user)) -> SettingsResponse:
    if not has_permission(current_user, "settings:view"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    from app.repositories import SchoolRepository
    school_repo = SchoolRepository(db)
    
    school = school_repo.get_by_slug("greenfield-college")
    
    return SettingsResponse(
        groups=[
            {
                "title": "School Identity",
                "description": "Your school's name, logo, and brand colors",
                "items": [
                    {"label": "School Name", "value": school.name if school else "Not configured"},
                    {"label": "Primary Color", "value": school.primary_color if school else "#14213D"},
                    {"label": "School Type", "value": school.school_type if school else "Secondary"},
                ]
            },
            {
                "title": "Payment Configuration",
                "description": "Payment gateway settings and fee structures",
                "items": [
                    {"label": "Paystack Enabled", "value": "No"},
                    {"label": "Flutterwave Enabled", "value": "No"},
                    {"label": "Default Currency", "value": "NGN"},
                ]
            },
            {
                "title": "Communication",
                "description": "Email, SMS, and WhatsApp sender profiles",
                "items": [
                    {"label": "Email Sender", "value": "noreply@greenfieldcollege.ng"},
                    {"label": "SMS Gateway", "value": "Not configured"},
                    {"label": "WhatsApp Business", "value": "Not configured"},
                ]
            }
        ]
    )

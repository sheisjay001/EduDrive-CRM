from app.core.auth import authenticate_user, create_tokens_for_user
from app.schemas.crm import (
    ActivityItem,
    AdmissionsResponse,
    AuthRequest,
    AuthResponse,
    AuthUser,
    AuthRefreshRequest,
    CampaignItem,
    DashboardResponse,
    DebtorItem,
    FeeStructureItem,
    FeeStructuresResponse,
    FamilyDetailResponse,
    FamiliesResponse,
    FinanceResponse,
    FinanceSummary,
    HelpdeskResponse,
    HouseholdItem,
    InvoiceDetailLineItem,
    InvoiceDetailResponse,
    InvoiceItem,
    KpiCard,
    BroadcastRequest,
    ConvertLeadRequest,
    ConvertLeadResponse,
    FeeStructuresResponse,
    FlutterwaveInitResponse,
    InvoiceCreateRequest,
    InvoiceDetailResponse,
    LeadCreateRequest,
    LeadDetailResponse,
    LeadItem,
    LeadUpdateRequest,
    MessageTemplateItem,
    MessageTemplatesResponse,
    MessagingMetric,
    MessagingResponse,
    ParentDetailResponse,
    ParentItem,
    ParentsResponse,
    PaystackInitResponse,
    PaymentRecord,
    ReportCard,
    ReportsResponse,
    ReportResponse,
    SettingGroup,
    SettingItem,
    SettingsResponse,
    StaffMember,
    StaffMetric,
    StaffResponse,
    StageCard,
    StudentDetailResponse,
    StudentItem,
    StudentsResponse,
    TicketCreateRequest,
    TicketDetailResponse,
    TicketItem,
    TicketUpdateRequest,
)


PIPELINE = [
    StageCard(stage="New Leads", count=42, value="NGN 5.2M", nextAction="Call within 2 hours"),
    StageCard(stage="Tour Scheduled", count=28, value="NGN 3.7M", nextAction="Confirm attendance"),
    StageCard(stage="Assessment Booked", count=31, value="NGN 4.1M", nextAction="Share prep pack"),
    StageCard(stage="Offered", count=19, value="NGN 2.8M", nextAction="Issue enrollment invoice"),
]

LEADS_BY_ID = {
    "LD-104": LeadDetailResponse(
        id="LD-104",
        childName="David Ume",
        parentName="Mrs. Ume",
        parentEmail="ume.family@example.com",
        parentPhone="+2348090000001",
        source="Website form",
        stage="New Leads",
        classInterest="Primary 2",
        followUp="Today, 3:00 PM",
        notes="First inquiry from parent. Confirmed interest in afternoon tuition.",
        createdAt="2026-07-08T09:14:00Z",
    ),
    "LD-098": LeadDetailResponse(
        id="LD-098",
        childName="Amina Bello",
        parentName="Mr. Bello",
        parentEmail="bello.family@example.com",
        parentPhone="+2348090000002",
        source="Referral",
        stage="Tour Scheduled",
        classInterest="Nursery 2",
        followUp="Tomorrow, 10:30 AM",
        notes="Referral from church contact. Needs scholarship information.",
        createdAt="2026-07-04T15:20:00Z",
    ),
}

FAMILIES_BY_ID = {
    "FM-001": FamilyDetailResponse(
        id="FM-001",
        householdName="Adeyemi Household",
        guardians=["Mrs. Adeyemi", "Mr. Adeyemi"],
        students=["Praise Adeyemi", "Joshua Adeyemi", "Faith Adeyemi"],
        balance="NGN 350,000",
        status="Payment plan active",
        lastPayment="2026-07-20",
        openTickets=1,
        notes="Monthly payment plan agreed, transport ticket open.",
    ),
    "FM-002": FamilyDetailResponse(
        id="FM-002",
        householdName="Bello Family",
        guardians=["Mrs. Bello"],
        students=["Mubarak Bello", "Aisha Bello"],
        balance="NGN 0",
        status="Up to date",
        lastPayment="2026-07-14",
        openTickets=0,
        notes="No outstanding finance issues. Parent prefers SMS reminders.",
    ),
}

STUDENTS_BY_ID = {
    "ST-2034": StudentDetailResponse(
        id="ST-2034",
        fullName="Praise Adeyemi",
        className="Primary 4 Gold",
        guardian="Mrs. Adeyemi",
        attendance="96%",
        behaviour="Excellent",
        medicalFlag="Asthma action plan",
        nextAssessment="2026-08-05",
        feeStatus="Paid in full",
        documents=["Admission form", "Medical clearance"],
    ),
    "ST-1945": StudentDetailResponse(
        id="ST-1945",
        fullName="Mubarak Bello",
        className="Nursery 2 Blue",
        guardian="Mrs. Bello",
        attendance="91%",
        behaviour="Good",
        medicalFlag="None",
        nextAssessment="2026-08-03",
        feeStatus="Part paid",
        documents=["Admission form"],
    ),
}

PARENTS_BY_ID = {
    "PR-001": ParentDetailResponse(
        id="PR-001",
        name="Mrs. Adeyemi",
        relationship="Mother",
        phone="+2348090000003",
        email="mrs.adeyemi@example.com",
        preferredChannel="whatsapp",
        students=["Praise Adeyemi", "Joshua Adeyemi"],
        lastActivity="Payment reminder sent yesterday",
        notes="Primary billing contact; prefers WhatsApp updates.",
    ),
    "PR-002": ParentDetailResponse(
        id="PR-002",
        name="Mr. Bello",
        relationship="Father",
        phone="+2348090000004",
        email="mr.bello@example.com",
        preferredChannel="email",
        students=["Mubarak Bello"],
        lastActivity="Shared fee schedule via email two days ago",
        notes="Responds better to email and official messages.",
    ),
}

PARENT_LIST = [
    ParentItem(
        id="PR-001",
        name="Mrs. Adeyemi",
        relationship="Mother",
        studentName="Praise Adeyemi",
        phone="+2348090000003",
        email="mrs.adeyemi@example.com",
        status="Active",
    ),
    ParentItem(
        id="PR-002",
        name="Mr. Bello",
        relationship="Father",
        studentName="Mubarak Bello",
        phone="+2348090000004",
        email="mr.bello@example.com",
        status="Active",
    ),
]

TICKETS_BY_ID = {
    "TK-310": TicketDetailResponse(
        id="TK-310",
        subject="Bus route delay complaint",
        parent="Mrs. Ekanem",
        priority="High",
        assignee="Paul Nwosu",
        sla="2h remaining",
        status="In progress",
        description="Parent reported the morning bus arrived 35 minutes late and students missed registration.",
        createdAt="2026-07-29T08:20:00Z",
        timeline=[
            {"time": "08:20", "note": "Ticket submitted"},
            {"time": "09:15", "note": "Assigned to transport coordinator"},
            {"time": "10:04", "note": "Driver contacted for route update"},
        ],
    ),
    "TK-299": TicketDetailResponse(
        id="TK-299",
        subject="Receipt not received",
        parent="Mrs. Adeyemi",
        priority="Urgent",
        assignee="Bursar Team",
        sla="45m remaining",
        status="Assigned",
        description="Receipt for the latest fee payment did not arrive in the parent’s email inbox.",
        createdAt="2026-07-28T14:45:00Z",
        timeline=[
            {"time": "14:45", "note": "Ticket created"},
            {"time": "15:10", "note": "Bursar asked for email verification"},
        ],
    ),
}

INVOICES_BY_ID = {
    "INV-3001": InvoiceDetailResponse(
        id="INV-3001",
        student="Praise Adeyemi",
        term="2026 Third Term",
        amountDue="NGN 620,000",
        amountPaid="NGN 620,000",
        dueDate="2026-07-14",
        status="Paid",
        issuedAt="2026-07-01T10:00:00Z",
        lineItems=[
            InvoiceDetailLineItem(code="FEE-TU", description="Tuition fee", amount="NGN 500,000"),
            InvoiceDetailLineItem(code="FEE-TR", description="Transport service", amount="NGN 90,000"),
            InvoiceDetailLineItem(code="FEE-EX", description="Exam fee", amount="NGN 30,000"),
        ],
        payments=[
            PaymentRecord(method="Bank transfer", amount="NGN 620,000", paidAt="2026-07-14T09:30:00Z"),
        ],
    ),
    "INV-2974": InvoiceDetailResponse(
        id="INV-2974",
        student="Favour Okafor",
        term="2026 Third Term",
        amountDue="NGN 710,000",
        amountPaid="NGN 0",
        dueDate="2026-07-25",
        status="Overdue",
        issuedAt="2026-06-30T11:05:00Z",
        lineItems=[
            InvoiceDetailLineItem(code="FEE-TU", description="Tuition fee", amount="NGN 560,000"),
            InvoiceDetailLineItem(code="FEE-TR", description="Transport service", amount="NGN 100,000"),
            InvoiceDetailLineItem(code="FEE-MT", description="Materials", amount="NGN 50,000"),
        ],
        payments=[],
    ),
}

FEE_STRUCTURES = [
    FeeStructureItem(id="FS-001", className="Primary 4 Gold", termName="Third Term", title="Standard tuition and transport", amount="NGN 620,000", dueDays=14),
    FeeStructureItem(id="FS-002", className="Nursery 2 Blue", termName="Third Term", title="Tuition and meals", amount="NGN 430,000", dueDays=14),
    FeeStructureItem(id="FS-003", className="JSS 1 Red", termName="Third Term", title="Tuition, book levy, exam fees", amount="NGN 710,000", dueDays=14),
]

MESSAGE_TEMPLATES = [
    MessageTemplateItem(id="MT-001", name="Fee reminder", channel="WhatsApp", useCase="Debtor follow-up", lastEdited="2026-07-25"),
    MessageTemplateItem(id="MT-002", name="Admission tour invite", channel="Email", useCase="Lead nurture", lastEdited="2026-07-20"),
    MessageTemplateItem(id="MT-003", name="Support ticket update", channel="SMS", useCase="Help desk", lastEdited="2026-07-22"),
]


def login(payload: AuthRequest) -> AuthResponse:
    auth_user = authenticate_user(payload.email, payload.password)
    if auth_user is None:
        raise ValueError("Invalid login credentials")

    access_token, refresh_token = create_tokens_for_user(auth_user)
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
        user=auth_user,
    )


def refresh(user: AuthUser) -> AuthResponse:
    access_token, refresh_token = create_tokens_for_user(user)
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
        user=user,
    )


def get_dashboard() -> DashboardResponse:
    return DashboardResponse(
        schoolName="Greenfield College, Abuja",
        sessionLabel="2026 Third Term",
        kpis=[
            KpiCard(label="Revenue Collected", value="NGN 18.4M", change="+12.6% vs last term", tone="good"),
            KpiCard(label="Outstanding Fees", value="NGN 4.9M", change="183 families pending", tone="warn"),
            KpiCard(label="Active Admissions", value="148", change="31 assessment-ready", tone="neutral"),
            KpiCard(label="Open Tickets", value="19", change="4 breach risk", tone="danger"),
        ],
        pipeline=PIPELINE,
        activity=[
            ActivityItem(title="Bursar posted 14 payments", subtitle="18 invoices reconciled before noon", time="12 mins ago", tone="good"),
            ActivityItem(title="Admissions follow-up due", subtitle="6 leads from church referral campaign", time="24 mins ago", tone="warn"),
            ActivityItem(title="Parent complaint escalated", subtitle="Transport ticket assigned to operations", time="49 mins ago", tone="danger"),
            ActivityItem(title="Teacher attendance synced", subtitle="Primary 5A and 5B updated for the day", time="1 hr ago", tone="neutral"),
        ],
        revenueTrend=[
            {"name": "Mon", "value": 2.4},
            {"name": "Tue", "value": 3.1},
            {"name": "Wed", "value": 2.8},
            {"name": "Thu", "value": 4.2},
            {"name": "Fri", "value": 5.9},
        ],
    )


def get_admissions() -> AdmissionsResponse:
    return AdmissionsResponse(
        pipeline=PIPELINE,
        leads=[
            LeadItem(id="LD-104", childName="David Ume", parentName="Mrs. Ume", source="Website form", stage="New Leads", classInterest="Primary 2", followUp="Today, 3:00 PM"),
            LeadItem(id="LD-098", childName="Amina Bello", parentName="Mr. Bello", source="Referral", stage="Tour Scheduled", classInterest="Nursery 2", followUp="Tomorrow, 10:30 AM"),
            LeadItem(id="LD-087", childName="Favour Okeke", parentName="Mrs. Okeke", source="Instagram", stage="Assessment Booked", classInterest="JSS 1", followUp="Friday, 8:00 AM"),
            LeadItem(id="LD-081", childName="Daniel Effiong", parentName="Mr. Effiong", source="Walk-in", stage="Offered", classInterest="Primary 5", followUp="Awaiting payment"),
        ],
    )


def get_lead_detail(lead_id: str) -> LeadDetailResponse:
    return LEADS_BY_ID.get(
        lead_id,
        LeadDetailResponse(
            id=lead_id,
            childName="Unknown lead",
            parentName="Unknown parent",
            parentEmail=None,
            parentPhone=None,
            source="Unknown",
            stage="New Leads",
            classInterest="Unknown",
            followUp="TBD",
            notes="Lead details are not available in the demo store.",
            createdAt="2026-01-01T00:00:00Z",
        ),
    )


def create_lead(payload: LeadCreateRequest, school_id: str) -> LeadDetailResponse:
    return LeadDetailResponse(
        id="LD-999",
        childName=f"{payload.firstName} {payload.lastName}",
        parentName=payload.parentName or "Unknown parent",
        parentEmail=payload.parentEmail,
        parentPhone=payload.parentPhone,
        source=payload.source,
        stage=payload.stage,
        classInterest=payload.interestedClass or "Unknown",
        followUp=payload.followUpAt or "TBD",
        notes="Lead created by the admissions workflow.",
        createdAt="2026-07-30T10:00:00Z",
    )


def update_lead(lead_id: str, payload: LeadUpdateRequest) -> LeadDetailResponse:
    original = get_lead_detail(lead_id)
    return LeadDetailResponse(
        id=original.id,
        childName=original.childName,
        parentName=original.parentName,
        parentEmail=original.parentEmail,
        parentPhone=original.parentPhone,
        source=original.source,
        stage=payload.stage or original.stage,
        classInterest=original.classInterest,
        followUp=payload.followUpAt or original.followUp,
        notes=payload.lostReason or original.notes,
        createdAt=original.createdAt,
    )


def get_families() -> FamiliesResponse:
    return FamiliesResponse(
        households=[
            HouseholdItem(id="FM-001", householdName="Adeyemi Household", guardians=["Mrs. Adeyemi", "Mr. Adeyemi"], students=3, balance="NGN 350,000", status="Payment plan active"),
            HouseholdItem(id="FM-002", householdName="Bello Family", guardians=["Mrs. Bello"], students=2, balance="NGN 0", status="Up to date"),
            HouseholdItem(id="FM-003", householdName="Okafor Family", guardians=["Mr. Okafor", "Mrs. Okafor"], students=1, balance="NGN 125,000", status="Reminder due"),
        ]
    )


def get_family_detail(family_id: str) -> FamilyDetailResponse:
    return FAMILIES_BY_ID.get(
        family_id,
        FamilyDetailResponse(
            id=family_id,
            householdName="Unknown household",
            guardians=[],
            students=[],
            balance="NGN 0",
            status="Unknown",
            lastPayment="N/A",
            openTickets=0,
            notes="Household details are not available in the demo store.",
        ),
    )


def get_parents() -> ParentsResponse:
    return ParentsResponse(parents=PARENT_LIST)


def get_parent_detail(parent_id: str) -> ParentDetailResponse:
    return PARENTS_BY_ID.get(
        parent_id,
        ParentDetailResponse(
            id=parent_id,
            name="Unknown parent",
            relationship="Unknown",
            phone="Unknown",
            email="unknown@example.com",
            preferredChannel="email",
            students=[],
            lastActivity="No recent activity",
            notes="Parent details are not available in the demo store.",
        ),
    )


def get_ticket_detail(ticket_id: str) -> TicketDetailResponse:
    return TICKETS_BY_ID.get(
        ticket_id,
        TicketDetailResponse(
            id=ticket_id,
            subject="Unknown ticket",
            parent="Unknown",
            priority="Medium",
            assignee="Unassigned",
            sla="Not set",
            status="Open",
            description="Ticket details are not available in the demo store.",
            createdAt="2026-01-01T00:00:00Z",
            timeline=[{"time": "00:00", "note": "No events recorded."}],
        ),
    )


def get_invoice_detail(invoice_id: str) -> InvoiceDetailResponse:
    return INVOICES_BY_ID.get(
        invoice_id,
        InvoiceDetailResponse(
            id=invoice_id,
            student="Unknown student",
            term="Unknown term",
            amountDue="NGN 0",
            amountPaid="NGN 0",
            dueDate="N/A",
            status="Unknown",
            issuedAt="2026-01-01T00:00:00Z",
            lineItems=[InvoiceDetailLineItem(code="N/A", description="No invoice details available", amount="NGN 0")],
            payments=[],
        ),
    )


def get_fee_structures() -> FeeStructuresResponse:
    return FeeStructuresResponse(items=FEE_STRUCTURES)


def get_message_templates() -> MessageTemplatesResponse:
    return MessageTemplatesResponse(templates=MESSAGE_TEMPLATES)


def broadcast_message(payload: BroadcastRequest) -> dict[str, str]:
    return {"status": "queued", "message": "Broadcast request received."}


def init_paystack() -> PaystackInitResponse:
    return PaystackInitResponse(
        authorization_url="https://paystack.com/pay/demo-reference",
        reference="PSK-REF-12345",
    )


def init_flutterwave() -> FlutterwaveInitResponse:
    return FlutterwaveInitResponse(
        checkout_url="https://flutterwave.com/checkout/demo-reference",
        reference="FLW-REF-12345",
    )


def handle_paystack_webhook(payload: dict) -> dict[str, str]:
    return {"status": "processed", "event": payload.get("event", "unknown")}


def handle_flutterwave_webhook(payload: dict) -> dict[str, str]:
    return {"status": "processed", "event": payload.get("event", "unknown")}


def create_invoice(payload: InvoiceCreateRequest, school_id: str) -> InvoiceDetailResponse:
    return InvoiceDetailResponse(
        id="INV-9999",
        student="New Student",
        term=payload.term,
        amountDue=f"NGN {payload.amountDue:,.2f}",
        amountPaid="NGN 0",
        dueDate=payload.dueDate,
        status="Issued",
        issuedAt="2026-07-30T10:00:00Z",
        lineItems=[
            InvoiceDetailLineItem(code=item.code, description=item.description, amount=f"NGN {item.amount:,.2f}") for item in payload.lineItems
        ],
        payments=[],
    )


def record_payment(payload: PaymentRecord) -> PaymentRecord:
    return payload


def create_ticket(payload: TicketCreateRequest) -> TicketDetailResponse:
    return TicketDetailResponse(
        id="TK-399",
        subject=payload.subject,
        parent=payload.parentId or "Unknown parent",
        priority=payload.priority,
        assignee=payload.assigneeId or "Unassigned",
        sla=payload.slaDueAt or "Not set",
        status="Open",
        description=payload.description or "No description provided.",
        createdAt="2026-07-30T10:00:00Z",
        timeline=[{"time": "10:00", "note": "Ticket created."}],
    )


def update_ticket(ticket_id: str, payload: TicketUpdateRequest) -> TicketDetailResponse:
    existing = get_ticket_detail(ticket_id)
    return TicketDetailResponse(
        id=existing.id,
        subject=existing.subject,
        parent=existing.parent,
        priority=payload.priority or existing.priority,
        assignee=payload.assigneeId or existing.assignee,
        sla=payload.slaDueAt or existing.sla,
        status=payload.status or existing.status,
        description=existing.description,
        createdAt=existing.createdAt,
        timeline=existing.timeline + [{"time": "10:30", "note": "Ticket updated."}],
    )


def get_report(report_name: str) -> ReportResponse:
    return ReportResponse(
        reportName=report_name,
        data=[
            {"label": "Metric A", "value": 72},
            {"label": "Metric B", "value": 28},
        ],
    )


def convert_lead(lead_id: str, payload: ConvertLeadRequest) -> ConvertLeadResponse:
    return ConvertLeadResponse(
        leadId=lead_id,
        familyId="FM-004",
        studentId="ST-2099",
        status="Converted",
    )


def get_students() -> StudentsResponse:
    return StudentsResponse(
        students=[
            StudentItem(id="ST-2034", fullName="Praise Adeyemi", className="Primary 4 Gold", guardian="Mrs. Adeyemi", attendance="96%", behaviour="Excellent", medicalFlag="Asthma action plan"),
            StudentItem(id="ST-1945", fullName="Mubarak Bello", className="Nursery 2 Blue", guardian="Mrs. Bello", attendance="91%", behaviour="Good", medicalFlag="None"),
            StudentItem(id="ST-1876", fullName="Favour Okafor", className="JSS 1 Red", guardian="Mr. Okafor", attendance="89%", behaviour="Needs follow-up", medicalFlag="Nut allergy"),
        ]
    )


def get_student_detail(student_id: str) -> StudentDetailResponse:
    return STUDENTS_BY_ID.get(
        student_id,
        StudentDetailResponse(
            id=student_id,
            fullName="Unknown student",
            className="Unknown",
            guardian="Unknown",
            attendance="0%",
            behaviour="Unknown",
            medicalFlag="None",
            nextAssessment="TBD",
            feeStatus="Unknown",
            documents=[],
        ),
    )


def get_finance() -> FinanceResponse:
    return FinanceResponse(
        summary=FinanceSummary(totalBilled="NGN 23.3M", totalCollected="NGN 18.4M", overdue="NGN 4.9M", collectionRate="79%"),
        invoices=[
            InvoiceItem(id="INV-3001", student="Praise Adeyemi", term="2026 Third Term", amountDue="NGN 620,000", amountPaid="NGN 620,000", dueDate="Paid on Jul 14", status="Paid"),
            InvoiceItem(id="INV-2986", student="Mubarak Bello", term="2026 Third Term", amountDue="NGN 430,000", amountPaid="NGN 230,000", dueDate="Due Aug 02", status="Part paid"),
            InvoiceItem(id="INV-2974", student="Favour Okafor", term="2026 Third Term", amountDue="NGN 710,000", amountPaid="NGN 0", dueDate="Overdue by 5 days", status="Overdue"),
        ],
        debtors=[
            DebtorItem(student="Favour Okafor", className="JSS 1 Red", balance="NGN 710,000", aging="0-15 days", lastContact="WhatsApp reminder yesterday"),
            DebtorItem(student="Daniel Effiong", className="Primary 5 Gold", balance="NGN 290,000", aging="16-30 days", lastContact="Bursar phone call today"),
            DebtorItem(student="Mercy Aliyu", className="Primary 2 Green", balance="NGN 185,000", aging="31+ days", lastContact="Payment plan requested"),
        ],
    )


def get_messaging() -> MessagingResponse:
    return MessagingResponse(
        metrics=[
            MessagingMetric(channel="Email", sent="2,184", openRate="63%", delivery="99.1%"),
            MessagingMetric(channel="SMS", sent="1,420", openRate="98%", delivery="96.4%"),
            MessagingMetric(channel="WhatsApp", sent="845", openRate="91%", delivery="93.8%"),
        ],
        campaigns=[
            CampaignItem(title="Third term fee reminder", audience="Debtors 0-15 days", channel="WhatsApp + Email", status="In progress", sentAt="Today, 8:00 AM"),
            CampaignItem(title="Assessment invitation", audience="Qualified leads", channel="Email", status="Completed", sentAt="Yesterday, 5:30 PM"),
            CampaignItem(title="Parent town hall notice", audience="All active parents", channel="SMS", status="Scheduled", sentAt="Tomorrow, 7:00 AM"),
        ],
    )


def get_helpdesk() -> HelpdeskResponse:
    return HelpdeskResponse(
        tickets=[
            TicketItem(id="TK-310", subject="Bus route delay complaint", parent="Mrs. Ekanem", priority="High", assignee="Paul Nwosu", sla="2h remaining", status="In progress"),
            TicketItem(id="TK-305", subject="Portal password reset", parent="Mr. Bello", priority="Medium", assignee="Grace Udo", sla="Resolved within SLA", status="Resolved"),
            TicketItem(id="TK-299", subject="Receipt not received", parent="Mrs. Adeyemi", priority="Urgent", assignee="Bursar Team", sla="45m remaining", status="Assigned"),
        ]
    )


def get_staff() -> StaffResponse:
    return StaffResponse(
        metrics=[
            StaffMetric(label="Staff On Time", value="91%", note="Attendance check by 7:45 AM"),
            StaffMetric(label="Average Ticket Response", value="1h 18m", note="Help desk and bursary combined"),
            StaffMetric(label="Parent Reply Score", value="4.6/5", note="Last 30 days sentiment"),
        ],
        people=[
            StaffMember(name="Mrs. Yusuf", role="Admissions Officer", attendance="98%", responseTime="38m", performance="Top converter"),
            StaffMember(name="Mr. Okoro", role="Bursar", attendance="95%", responseTime="52m", performance="Strong collections"),
            StaffMember(name="Ms. Gloria", role="Help Desk", attendance="97%", responseTime="29m", performance="High satisfaction"),
        ],
    )


def get_reports() -> ReportsResponse:
    return ReportsResponse(
        cards=[
            ReportCard(title="Admissions Conversion", insight="Lead-to-enrollment improved after faster tour confirmation.", value="38%"),
            ReportCard(title="Fee Recovery", insight="Collections are strongest within the first 10 days after reminders.", value="79%"),
            ReportCard(title="Parent Engagement", insight="WhatsApp remains the highest-response operational channel.", value="91% reach"),
        ],
        admissionsTrend=[
            {"name": "Jan", "value": 18},
            {"name": "Feb", "value": 24},
            {"name": "Mar", "value": 27},
            {"name": "Apr", "value": 31},
            {"name": "May", "value": 38},
        ],
        collectionsTrend=[
            {"name": "Week 1", "value": 4.8},
            {"name": "Week 2", "value": 6.2},
            {"name": "Week 3", "value": 3.7},
            {"name": "Week 4", "value": 7.1},
        ],
    )


def get_settings() -> SettingsResponse:
    return SettingsResponse(
        groups=[
            SettingGroup(
                title="School Identity",
                description="Brand and academic identity used across parent-facing channels.",
                items=[
                    SettingItem(label="School name", value="Greenfield College, Abuja"),
                    SettingItem(label="Current term", value="2026 Third Term"),
                    SettingItem(label="Primary contact", value="hello@greenfieldcollege.ng"),
                ],
            ),
            SettingGroup(
                title="Payment Integrations",
                description="Providers configured for collection, verification, and receipt delivery.",
                items=[
                    SettingItem(label="Paystack", value="Configured for live verification"),
                    SettingItem(label="Flutterwave", value="Sandbox credentials pending"),
                    SettingItem(label="Offline collection", value="Bank transfer and cash enabled"),
                ],
            ),
            SettingGroup(
                title="Communication Channels",
                description="Messaging channels and sender profiles for operational communication.",
                items=[
                    SettingItem(label="Brevo sender", value="accounts@greenfieldcollege.ng"),
                    SettingItem(label="Termii sender", value="Greenfield"),
                    SettingItem(label="WhatsApp line", value="Admissions and finance active"),
                ],
            ),
        ]
    )

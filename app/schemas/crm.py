from pydantic import BaseModel, EmailStr


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class AuthRefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str


class AuthUser(BaseModel):
    id: str
    schoolId: str
    role: str
    fullName: str
    email: EmailStr


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUser


class KpiCard(BaseModel):
    label: str
    value: str
    change: str
    tone: str


class ActivityItem(BaseModel):
    title: str
    subtitle: str
    time: str
    tone: str


class StageCard(BaseModel):
    stage: str
    count: int
    value: str
    nextAction: str


class DashboardResponse(BaseModel):
    schoolName: str
    sessionLabel: str
    kpis: list[KpiCard]
    pipeline: list[StageCard]
    activity: list[ActivityItem]
    revenueTrend: list[dict[str, float | str]]


class LeadItem(BaseModel):
    id: str
    childName: str
    parentName: str
    source: str
    stage: str
    classInterest: str
    followUp: str


class LeadDetailResponse(BaseModel):
    id: str
    childName: str
    parentName: str
    parentEmail: str | None = None
    parentPhone: str | None = None
    source: str
    stage: str
    classInterest: str
    followUp: str
    notes: str
    createdAt: str


class ConvertLeadRequest(BaseModel):
    familyName: str
    primaryGuardian: str
    studentFirstName: str
    studentLastName: str
    studentGender: str | None = None
    dateOfBirth: str | None = None
    admittedClass: str | None = None


class ConvertLeadResponse(BaseModel):
    leadId: str
    familyId: str
    studentId: str
    status: str


class LeadCreateRequest(BaseModel):
    firstName: str
    lastName: str
    parentName: str | None = None
    parentPhone: str | None = None
    parentEmail: EmailStr | None = None
    source: str
    stage: str
    interestedClass: str | None = None
    followUpAt: str | None = None


class LeadUpdateRequest(BaseModel):
    stage: str | None = None
    followUpAt: str | None = None
    lostReason: str | None = None


class InvoiceLineItemRequest(BaseModel):
    code: str
    description: str
    amount: float


class InvoiceCreateRequest(BaseModel):
    studentId: str
    term: str
    amountDue: float
    dueDate: str
    lineItems: list[InvoiceLineItemRequest]


class PaymentRecord(BaseModel):
    invoiceId: str
    amount: float
    method: str
    reference: str | None = None
    paidAt: str


class PaystackInitResponse(BaseModel):
    authorization_url: str
    reference: str


class FlutterwaveInitResponse(BaseModel):
    checkout_url: str
    reference: str


class BroadcastRequest(BaseModel):
    audience: str
    channel: str
    templateId: str
    message: str | None = None


class TicketCreateRequest(BaseModel):
    parentId: str | None = None
    familyId: str | None = None
    subject: str
    description: str | None = None
    priority: str
    assigneeId: str | None = None
    slaDueAt: str | None = None


class TicketUpdateRequest(BaseModel):
    status: str | None = None
    priority: str | None = None
    assigneeId: str | None = None
    slaDueAt: str | None = None


class ReportResponse(BaseModel):
    reportName: str
    data: list[dict[str, str | int | float]]


class AdmissionsResponse(BaseModel):
    leads: list[LeadItem]
    pipeline: list[StageCard]


class HouseholdItem(BaseModel):
    id: str
    householdName: str
    guardians: list[str]
    students: int
    balance: str
    status: str


class FamilyDetailResponse(BaseModel):
    id: str
    householdName: str
    guardians: list[str]
    students: list[str]
    balance: str
    status: str
    lastPayment: str
    openTickets: int
    notes: str


class ParentItem(BaseModel):
    id: str
    name: str
    relationship: str
    studentName: str
    phone: str
    email: str
    status: str


class ParentDetailResponse(BaseModel):
    id: str
    name: str
    relationship: str
    phone: str
    email: EmailStr
    preferredChannel: str
    students: list[str]
    lastActivity: str
    notes: str


class FamiliesResponse(BaseModel):
    households: list[HouseholdItem]


class StudentItem(BaseModel):
    id: str
    fullName: str
    className: str
    guardian: str
    attendance: str
    behaviour: str
    medicalFlag: str


class StudentDetailResponse(BaseModel):
    id: str
    fullName: str
    className: str
    guardian: str
    attendance: str
    behaviour: str
    medicalFlag: str
    nextAssessment: str
    feeStatus: str
    documents: list[str]


class StudentsResponse(BaseModel):
    students: list[StudentItem]


class ParentsResponse(BaseModel):
    parents: list[ParentItem]


class FinanceSummary(BaseModel):
    totalBilled: str
    totalCollected: str
    overdue: str
    collectionRate: str


class InvoiceItem(BaseModel):
    id: str
    student: str
    term: str
    amountDue: str
    amountPaid: str
    dueDate: str
    status: str


class DebtorItem(BaseModel):
    student: str
    className: str
    balance: str
    aging: str
    lastContact: str


class FinanceResponse(BaseModel):
    summary: FinanceSummary
    invoices: list[InvoiceItem]
    debtors: list[DebtorItem]


class PaymentItem(BaseModel):
    id: str
    invoiceId: str
    student: str
    amount: str
    method: str
    paidAt: str
    status: str


class PaymentsResponse(BaseModel):
    payments: list[PaymentItem]


class InvoiceListResponse(BaseModel):
    invoices: list[InvoiceItem]


class BroadcastItem(BaseModel):
    id: str
    title: str
    audience: str
    channel: str
    status: str
    scheduledAt: str


class BroadcastsResponse(BaseModel):
    broadcasts: list[BroadcastItem]


class CalendarEvent(BaseModel):
    id: str
    title: str
    date: str
    time: str
    location: str
    status: str


class CalendarResponse(BaseModel):
    events: list[CalendarEvent]


class FeeStructureItem(BaseModel):
    id: str
    className: str
    termName: str
    title: str
    amount: str
    dueDays: int


class FeeStructuresResponse(BaseModel):
    items: list[FeeStructureItem]


class MessageTemplateItem(BaseModel):
    id: str
    name: str
    channel: str
    useCase: str
    lastEdited: str


class MessageTemplatesResponse(BaseModel):
    templates: list[MessageTemplateItem]


class MessagingMetric(BaseModel):
    channel: str
    sent: str
    openRate: str
    delivery: str


class CampaignItem(BaseModel):
    title: str
    audience: str
    channel: str
    status: str
    sentAt: str


class MessagingResponse(BaseModel):
    metrics: list[MessagingMetric]
    campaigns: list[CampaignItem]


class TicketItem(BaseModel):
    id: str
    subject: str
    parent: str
    priority: str
    assignee: str
    sla: str
    status: str


class TicketDetailResponse(BaseModel):
    id: str
    subject: str
    parent: str
    priority: str
    assignee: str
    sla: str
    status: str
    description: str
    createdAt: str
    timeline: list[dict[str, str]]


class HelpdeskResponse(BaseModel):
    tickets: list[TicketItem]


class InvoiceDetailLineItem(BaseModel):
    code: str
    description: str
    amount: str


class PaymentRecord(BaseModel):
    method: str
    amount: str
    paidAt: str


class InvoiceDetailResponse(BaseModel):
    id: str
    student: str
    term: str
    amountDue: str
    amountPaid: str
    dueDate: str
    status: str
    issuedAt: str
    lineItems: list[InvoiceDetailLineItem]
    payments: list[PaymentRecord]


class StaffMetric(BaseModel):
    label: str
    value: str
    note: str


class StaffMember(BaseModel):
    name: str
    role: str
    attendance: str
    responseTime: str
    performance: str


class StaffResponse(BaseModel):
    metrics: list[StaffMetric]
    people: list[StaffMember]


class ReportCard(BaseModel):
    title: str
    insight: str
    value: str


class ReportsResponse(BaseModel):
    cards: list[ReportCard]
    admissionsTrend: list[dict[str, float | str]]
    collectionsTrend: list[dict[str, float | str]]


class SettingItem(BaseModel):
    label: str
    value: str


class SettingGroup(BaseModel):
    title: str
    description: str
    items: list[SettingItem]


class SettingsResponse(BaseModel):
    groups: list[SettingGroup]

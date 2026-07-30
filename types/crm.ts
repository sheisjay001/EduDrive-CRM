export type StatusTone = "neutral" | "good" | "warn" | "danger";

export type KpiCard = {
  label: string;
  value: string;
  change: string;
  tone: StatusTone;
};

export type ActivityItem = {
  title: string;
  subtitle: string;
  time: string;
  tone: StatusTone;
};

export type StageCard = {
  stage: string;
  count: number;
  value: string;
  nextAction: string;
};

export type LeadItem = {
  id: string;
  childName: string;
  parentName: string;
  source: string;
  stage: string;
  classInterest: string;
  followUp: string;
};

export type LeadDetail = {
  id: string;
  childName: string;
  parentName: string;
  parentEmail?: string;
  parentPhone?: string;
  source: string;
  stage: string;
  classInterest: string;
  followUp: string;
  notes: string;
  createdAt: string;
};

export type FamilyDetail = {
  id: string;
  householdName: string;
  guardians: string[];
  students: string[];
  balance: string;
  status: string;
  lastPayment: string;
  openTickets: number;
  notes: string;
};

export type StudentDetail = {
  id: string;
  fullName: string;
  className: string;
  guardian: string;
  attendance: string;
  behaviour: string;
  medicalFlag: string;
  nextAssessment: string;
  feeStatus: string;
  documents: string[];
};

export type ParentItem = {
  id: string;
  name: string;
  relationship: string;
  studentName: string;
  phone: string;
  email: string;
  status: string;
};

export type ParentDetail = {
  id: string;
  name: string;
  relationship: string;
  phone: string;
  email: string;
  preferredChannel: string;
  students: string[];
  lastActivity: string;
  notes: string;
};

export type HouseholdItem = {
  id: string;
  householdName: string;
  guardians: string[];
  students: number;
  balance: string;
  status: string;
};

export type StudentItem = {
  id: string;
  fullName: string;
  className: string;
  guardian: string;
  attendance: string;
  behaviour: string;
  medicalFlag: string;
};

export type FinanceSummary = {
  totalBilled: string;
  totalCollected: string;
  overdue: string;
  collectionRate: string;
};

export type InvoiceItem = {
  id: string;
  student: string;
  term: string;
  amountDue: string;
  amountPaid: string;
  dueDate: string;
  status: string;
};

export type DebtorItem = {
  student: string;
  className: string;
  balance: string;
  aging: string;
  lastContact: string;
};

export type MessagingMetric = {
  channel: string;
  sent: string;
  openRate: string;
  delivery: string;
};

export type CampaignItem = {
  title: string;
  audience: string;
  channel: string;
  status: string;
  sentAt: string;
};

export type TicketItem = {
  id: string;
  subject: string;
  parent: string;
  priority: string;
  assignee: string;
  sla: string;
  status: string;
};

export type TicketDetail = {
  id: string;
  subject: string;
  parent: string;
  priority: string;
  assignee: string;
  sla: string;
  status: string;
  description: string;
  createdAt: string;
  timeline: Array<{ time: string; note: string }>;
};

export type InvoiceDetailLineItem = {
  code: string;
  description: string;
  amount: string;
};

export type PaymentRecord = {
  method: string;
  amount: string;
  paidAt: string;
};

export type InvoiceDetail = {
  id: string;
  student: string;
  term: string;
  amountDue: string;
  amountPaid: string;
  dueDate: string;
  status: string;
  issuedAt: string;
  lineItems: InvoiceDetailLineItem[];
  payments: PaymentRecord[];
};

export type FeeStructureItem = {
  id: string;
  className: string;
  termName: string;
  title: string;
  amount: string;
  dueDays: number;
};

export type MessageTemplateItem = {
  id: string;
  name: string;
  channel: string;
  useCase: string;
  lastEdited: string;
};

export type StaffMetric = {
  label: string;
  value: string;
  note: string;
};

export type StaffMember = {
  name: string;
  role: string;
  attendance: string;
  responseTime: string;
  performance: string;
};

export type ReportPoint = {
  name: string;
  value: number;
};

export type ReportCard = {
  title: string;
  insight: string;
  value: string;
};

export type SettingGroup = {
  title: string;
  description: string;
  items: Array<{
    label: string;
    value: string;
  }>;
};

export type AuthPayload = {
  email: string;
  password: string;
};

export type ForgotPasswordPayload = {
  email: string;
};

export type ResetPasswordPayload = {
  token: string;
  newPassword: string;
};

export type ConvertLeadPayload = {
  familyName: string;
  primaryGuardian: string;
  studentFirstName: string;
  studentLastName: string;
  studentGender?: string;
  dateOfBirth?: string;
  admittedClass?: string;
};

export type LeadCreateRequest = {
  firstName: string;
  lastName: string;
  parentName: string;
  parentPhone: string;
  parentEmail?: string;
  source: string;
  stage: string;
  interestedClass?: string;
  followUpAt?: string;
};

export type PasswordResetResponse = {
  message: string;
};

export type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
  user: {
    id: string;
    schoolId: string;
    role: string;
    fullName: string;
    email: string;
  };
};

export type DashboardResponse = {
  schoolName: string;
  sessionLabel: string;
  kpis: KpiCard[];
  pipeline: StageCard[];
  activity: ActivityItem[];
  revenueTrend: ReportPoint[];
};

export type AdmissionsResponse = {
  leads: LeadItem[];
  pipeline: StageCard[];
};

export type FamiliesResponse = {
  households: HouseholdItem[];
};

export type StudentsResponse = {
  students: StudentItem[];
};

export type ParentsResponse = {
  parents: ParentItem[];
};

export type TicketDetailResponse = {
  id: string;
  subject: string;
  parent: string;
  priority: string;
  assignee: string;
  sla: string;
  status: string;
  description: string;
  createdAt: string;
  timeline: Array<{ time: string; note: string }>;
};

export type InvoiceDetailResponse = {
  id: string;
  student: string;
  term: string;
  amountDue: string;
  amountPaid: string;
  dueDate: string;
  status: string;
  issuedAt: string;
  lineItems: InvoiceDetailLineItem[];
  payments: PaymentRecord[];
};

export type FeeStructuresResponse = {
  items: FeeStructureItem[];
};

export type MessageTemplatesResponse = {
  templates: MessageTemplateItem[];
};

export type ConvertLeadResponse = {
  leadId: string;
  familyId: string;
  studentId: string;
  status: string;
};

export type FinanceResponse = {
  summary: FinanceSummary;
  invoices: InvoiceItem[];
  debtors: DebtorItem[];
};

export type MessagingResponse = {
  metrics: MessagingMetric[];
  campaigns: CampaignItem[];
};

export type HelpdeskResponse = {
  tickets: TicketItem[];
};

export type StaffResponse = {
  metrics: StaffMetric[];
  people: StaffMember[];
};

export type ReportsResponse = {
  cards: ReportCard[];
  admissionsTrend: ReportPoint[];
  collectionsTrend: ReportPoint[];
};

export type SettingsResponse = {
  groups: SettingGroup[];
};

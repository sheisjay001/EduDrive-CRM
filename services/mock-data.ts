import type {
  AdmissionsResponse,
  DashboardResponse,
  FamiliesResponse,
  FinanceResponse,
  HelpdeskResponse,
  MessagingResponse,
  ParentsResponse,
  ReportsResponse,
  SettingsResponse,
  StaffResponse,
  StudentsResponse,
} from "@/types/crm";

export const dashboardData: DashboardResponse = {
  schoolName: "Greenfield College, Abuja",
  sessionLabel: "2026 Third Term",
  kpis: [
    { label: "Revenue Collected", value: "NGN 18.4M", change: "+12.6% vs last term", tone: "good" },
    { label: "Outstanding Fees", value: "NGN 4.9M", change: "183 families pending", tone: "warn" },
    { label: "Active Admissions", value: "148", change: "31 assessment-ready", tone: "neutral" },
    { label: "Open Tickets", value: "19", change: "4 breach risk", tone: "danger" },
  ],
  pipeline: [
    { stage: "New Leads", count: 42, value: "NGN 5.2M", nextAction: "Call within 2 hours" },
    { stage: "Tour Scheduled", count: 28, value: "NGN 3.7M", nextAction: "Confirm attendance" },
    { stage: "Assessment Booked", count: 31, value: "NGN 4.1M", nextAction: "Share prep pack" },
    { stage: "Offered", count: 19, value: "NGN 2.8M", nextAction: "Issue enrollment invoice" },
  ],
  activity: [
    { title: "Bursar posted 14 payments", subtitle: "18 invoices reconciled before noon", time: "12 mins ago", tone: "good" },
    { title: "Admissions follow-up due", subtitle: "6 leads from church referral campaign", time: "24 mins ago", tone: "warn" },
    { title: "Parent complaint escalated", subtitle: "Transport ticket assigned to operations", time: "49 mins ago", tone: "danger" },
    { title: "Teacher attendance synced", subtitle: "Primary 5A and 5B updated for the day", time: "1 hr ago", tone: "neutral" },
  ],
  revenueTrend: [
    { name: "Mon", value: 2.4 },
    { name: "Tue", value: 3.1 },
    { name: "Wed", value: 2.8 },
    { name: "Thu", value: 4.2 },
    { name: "Fri", value: 5.9 },
  ],
};

export const admissionsData: AdmissionsResponse = {
  pipeline: dashboardData.pipeline,
  leads: [
    { id: "LD-104", childName: "David Ume", parentName: "Mrs. Ume", source: "Website form", stage: "New Leads", classInterest: "Primary 2", followUp: "Today, 3:00 PM" },
    { id: "LD-098", childName: "Amina Bello", parentName: "Mr. Bello", source: "Referral", stage: "Tour Scheduled", classInterest: "Nursery 2", followUp: "Tomorrow, 10:30 AM" },
    { id: "LD-087", childName: "Favour Okeke", parentName: "Mrs. Okeke", source: "Instagram", stage: "Assessment Booked", classInterest: "JSS 1", followUp: "Friday, 8:00 AM" },
    { id: "LD-081", childName: "Daniel Effiong", parentName: "Mr. Effiong", source: "Walk-in", stage: "Offered", classInterest: "Primary 5", followUp: "Awaiting payment" },
  ],
};

export const familiesData: FamiliesResponse = {
  households: [
    { id: "FM-001", householdName: "Adeyemi Household", guardians: ["Mrs. Adeyemi", "Mr. Adeyemi"], students: 3, balance: "NGN 350,000", status: "Payment plan active" },
    { id: "FM-002", householdName: "Bello Family", guardians: ["Mrs. Bello"], students: 2, balance: "NGN 0", status: "Up to date" },
    { id: "FM-003", householdName: "Okafor Family", guardians: ["Mr. Okafor", "Mrs. Okafor"], students: 1, balance: "NGN 125,000", status: "Reminder due" },
  ],
};

export const studentsData: StudentsResponse = {
  students: [
    { id: "ST-2034", fullName: "Praise Adeyemi", className: "Primary 4 Gold", guardian: "Mrs. Adeyemi", attendance: "96%", behaviour: "Excellent", medicalFlag: "Asthma action plan" },
    { id: "ST-1945", fullName: "Mubarak Bello", className: "Nursery 2 Blue", guardian: "Mrs. Bello", attendance: "91%", behaviour: "Good", medicalFlag: "None" },
    { id: "ST-1876", fullName: "Favour Okafor", className: "JSS 1 Red", guardian: "Mr. Okafor", attendance: "89%", behaviour: "Needs follow-up", medicalFlag: "Nut allergy" },
  ],
};

export const parentsData: ParentsResponse = {
  parents: [
    { id: "PR-001", name: "Mrs. Adeyemi", relationship: "Mother", studentName: "Praise Adeyemi", phone: "+2348090000003", email: "mrs.adeyemi@example.com", status: "Active" },
    { id: "PR-002", name: "Mr. Bello", relationship: "Father", studentName: "Mubarak Bello", phone: "+2348090000004", email: "mr.bello@example.com", status: "Active" },
    { id: "PR-003", name: "Mrs. Okeke", relationship: "Mother", studentName: "Favour Okeke", phone: "+2348090000005", email: "mrs.okeke@example.com", status: "Active" },
  ],
};

export const financeData: FinanceResponse = {
  summary: {
    totalBilled: "NGN 23.3M",
    totalCollected: "NGN 18.4M",
    overdue: "NGN 4.9M",
    collectionRate: "79%",
  },
  invoices: [
    { id: "INV-3001", student: "Praise Adeyemi", term: "2026 Third Term", amountDue: "NGN 620,000", amountPaid: "NGN 620,000", dueDate: "Paid on Jul 14", status: "Paid" },
    { id: "INV-2986", student: "Mubarak Bello", term: "2026 Third Term", amountDue: "NGN 430,000", amountPaid: "NGN 230,000", dueDate: "Due Aug 02", status: "Part paid" },
    { id: "INV-2974", student: "Favour Okafor", term: "2026 Third Term", amountDue: "NGN 710,000", amountPaid: "NGN 0", dueDate: "Overdue by 5 days", status: "Overdue" },
  ],
  debtors: [
    { student: "Favour Okafor", className: "JSS 1 Red", balance: "NGN 710,000", aging: "0-15 days", lastContact: "WhatsApp reminder yesterday" },
    { student: "Daniel Effiong", className: "Primary 5 Gold", balance: "NGN 290,000", aging: "16-30 days", lastContact: "Bursar phone call today" },
    { student: "Mercy Aliyu", className: "Primary 2 Green", balance: "NGN 185,000", aging: "31+ days", lastContact: "Payment plan requested" },
  ],
};

export const messagingData: MessagingResponse = {
  metrics: [
    { channel: "Email", sent: "2,184", openRate: "63%", delivery: "99.1%" },
    { channel: "SMS", sent: "1,420", openRate: "98%", delivery: "96.4%" },
    { channel: "WhatsApp", sent: "845", openRate: "91%", delivery: "93.8%" },
  ],
  campaigns: [
    { title: "Third term fee reminder", audience: "Debtors 0-15 days", channel: "WhatsApp + Email", status: "In progress", sentAt: "Today, 8:00 AM" },
    { title: "Assessment invitation", audience: "Qualified leads", channel: "Email", status: "Completed", sentAt: "Yesterday, 5:30 PM" },
    { title: "Parent town hall notice", audience: "All active parents", channel: "SMS", status: "Scheduled", sentAt: "Tomorrow, 7:00 AM" },
  ],
};

export const helpdeskData: HelpdeskResponse = {
  tickets: [
    { id: "TK-310", subject: "Bus route delay complaint", parent: "Mrs. Ekanem", priority: "High", assignee: "Paul Nwosu", sla: "2h remaining", status: "In progress" },
    { id: "TK-305", subject: "Portal password reset", parent: "Mr. Bello", priority: "Medium", assignee: "Grace Udo", sla: "Resolved within SLA", status: "Resolved" },
    { id: "TK-299", subject: "Receipt not received", parent: "Mrs. Adeyemi", priority: "Urgent", assignee: "Bursar Team", sla: "45m remaining", status: "Assigned" },
  ],
};

export const staffData: StaffResponse = {
  metrics: [
    { label: "Staff On Time", value: "91%", note: "Attendance check by 7:45 AM" },
    { label: "Average Ticket Response", value: "1h 18m", note: "Help desk and bursary combined" },
    { label: "Parent Reply Score", value: "4.6/5", note: "Last 30 days sentiment" },
  ],
  people: [
    { name: "Mrs. Yusuf", role: "Admissions Officer", attendance: "98%", responseTime: "38m", performance: "Top converter" },
    { name: "Mr. Okoro", role: "Bursar", attendance: "95%", responseTime: "52m", performance: "Strong collections" },
    { name: "Ms. Gloria", role: "Help Desk", attendance: "97%", responseTime: "29m", performance: "High satisfaction" },
  ],
};

export const reportsData: ReportsResponse = {
  cards: [
    { title: "Admissions Conversion", insight: "Lead-to-enrollment improved after faster tour confirmation.", value: "38%" },
    { title: "Fee Recovery", insight: "Collections are strongest within the first 10 days after reminders.", value: "79%" },
    { title: "Parent Engagement", insight: "WhatsApp remains the highest-response operational channel.", value: "91% reach" },
  ],
  admissionsTrend: [
    { name: "Jan", value: 18 },
    { name: "Feb", value: 24 },
    { name: "Mar", value: 27 },
    { name: "Apr", value: 31 },
    { name: "May", value: 38 },
  ],
  collectionsTrend: [
    { name: "Week 1", value: 4.8 },
    { name: "Week 2", value: 6.2 },
    { name: "Week 3", value: 3.7 },
    { name: "Week 4", value: 7.1 },
  ],
};

export const settingsData: SettingsResponse = {
  groups: [
    {
      title: "School Identity",
      description: "Brand and academic identity used across parent-facing channels.",
      items: [
        { label: "School name", value: "Greenfield College, Abuja" },
        { label: "Current term", value: "2026 Third Term" },
        { label: "Primary contact", value: "hello@greenfieldcollege.ng" },
      ],
    },
    {
      title: "Payment Integrations",
      description: "Providers configured for collection, verification, and receipt delivery.",
      items: [
        { label: "Paystack", value: "Configured for live verification" },
        { label: "Flutterwave", value: "Sandbox credentials pending" },
        { label: "Offline collection", value: "Bank transfer and cash enabled" },
      ],
    },
    {
      title: "Communication Channels",
      description: "Messaging channels and sender profiles for operational communication.",
      items: [
        { label: "Brevo sender", value: "accounts@greenfieldcollege.ng" },
        { label: "Termii sender", value: "Greenfield" },
        { label: "WhatsApp line", value: "Admissions and finance active" },
      ],
    },
  ],
};

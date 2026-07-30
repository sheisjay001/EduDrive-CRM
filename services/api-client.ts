import {
  admissionsData,
  dashboardData,
  familiesData,
  financeData,
  helpdeskData,
  messagingData,
  reportsData,
  settingsData,
  staffData,
  studentsData,
} from "@/services/mock-data";
import { clearAuthTokens, getAccessToken, saveAuthTokens, saveUser } from "@/services/auth-storage";
import { supabase } from "@/lib/supabase";
import type {
  AdmissionsResponse,
  AuthPayload,
  AuthResponse,
  ConvertLeadPayload,
  ConvertLeadResponse,
  DashboardResponse,
  FeeStructuresResponse,
  ForgotPasswordPayload,
  InvoiceDetail,
  InvoiceItem,
  FamilyDetail,
  FamiliesResponse,
  FinanceResponse,
  HelpdeskResponse,
  LeadDetail,
  MessageTemplatesResponse,
  MessagingResponse,
  ParentDetail,
  ParentsResponse,
  PasswordResetResponse,
  ReportsResponse,
  ResetPasswordPayload,
  SettingsResponse,
  StaffResponse,
  StudentDetail,
  StudentsResponse,
  TicketDetailResponse,
  TicketItem,
} from "@/types/crm";


const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

async function request<T>(path: string, fallback: T, init?: RequestInit): Promise<T> {
  const accessToken = getAccessToken();
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthTokens();
    }
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export const apiClient = {
  async login(payload: AuthPayload) {
    // Use Supabase authentication
    const { data, error } = await supabase.auth.signInWithPassword({
      email: payload.email,
      password: payload.password,
    });

    if (error) {
      throw new Error(error.message);
    }

    if (!data.session) {
      throw new Error("No session returned");
    }

    // Get user role from backend using Supabase session
    const backendResponse = await request<AuthResponse>("/auth/login", {} as AuthResponse, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    // Save tokens and user info
    saveAuthTokens(data.session.access_token, data.session.refresh_token);
    saveUser(backendResponse.user);

    return backendResponse;
  },
  forgotPassword(payload: ForgotPasswordPayload) {
    return request<PasswordResetResponse>(
      "/auth/forgot-password",
      {} as PasswordResetResponse,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  },
  resetPassword(payload: ResetPasswordPayload) {
    return request<PasswordResetResponse>(
      "/auth/reset-password",
      {} as PasswordResetResponse,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  },
  getDashboard() {
    return request<DashboardResponse>("/dashboard/summary", {} as DashboardResponse);
  },
  getAdmissions() {
    return request<AdmissionsResponse>("/leads", {} as AdmissionsResponse);
  },
  getFamilies() {
    return request<FamiliesResponse>("/families", {} as FamiliesResponse);
  },
  getStudents() {
    return request<StudentsResponse>("/students", {} as StudentsResponse);
  },
  getFinance() {
    return request<FinanceResponse>("/finance/overview", {} as FinanceResponse);
  },
  getMessaging() {
    return request<MessagingResponse>("/messages/overview", {} as MessagingResponse);
  },
  getHelpdesk() {
    return request<HelpdeskResponse>("/tickets", {} as HelpdeskResponse);
  },
  getStaff() {
    return request<StaffResponse>("/staff/overview", {} as StaffResponse);
  },
  getReports() {
    return request<ReportsResponse>("/reports/overview", {} as ReportsResponse);
  },
  getSettings() {
    return request<SettingsResponse>("/settings/overview", {} as SettingsResponse);
  },
  getFeeStructures() {
    return request<FeeStructuresResponse>("/finance/fee-structures", {} as FeeStructuresResponse);
  },
  getMessageTemplates() {
    return request<MessageTemplatesResponse>("/messages/templates", {} as MessageTemplatesResponse);
  },
  convertLead(leadId: string, payload: ConvertLeadPayload) {
    return request<ConvertLeadResponse>(
      `/leads/${leadId}/convert`,
      {} as ConvertLeadResponse,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  },
  createLead(payload: any) {
    return request<{ id: string }>(
      "/leads",
      {} as { id: string },
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  },
  updateLeadStage(leadId: string, stage: string) {
    return request<{ id: string; stage: string }>(
      `/leads/${leadId}/stage`,
      {} as { id: string; stage: string },
      {
        method: "PATCH",
        body: JSON.stringify({ stage }),
      },
    );
  },
  getLead(leadId: string) {
    return request<LeadDetail>(`/leads/${leadId}`, {} as LeadDetail);
  },
  getFamily(familyId: string) {
    return request<FamilyDetail>(`/families/${familyId}`, {} as FamilyDetail);
  },
  getParents() {
    return request<ParentsResponse>("/parents", {} as ParentsResponse);
  },
  getParent(parentId: string) {
    return request<ParentDetail>(`/parents/${parentId}`, {} as ParentDetail);
  },
  getTicket(ticketId: string) {
    return request<TicketDetailResponse>(`/tickets/${ticketId}`, {} as TicketDetailResponse);
  },
  getInvoice(invoiceId: string) {
    return request<InvoiceDetail>(`/invoices/${invoiceId}`, {} as InvoiceDetail);
  },
  getStudent(studentId: string) {
    return request<StudentDetail>(`/students/${studentId}`, {} as StudentDetail);
  },
};

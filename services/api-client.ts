import { clearAuthTokens, getAccessToken, getRefreshToken, saveAuthTokens, saveUser } from "@/services/auth-storage";
import type {
  AdmissionsResponse,
  AuthPayload,
  AuthResponse,
  CBTExamCreateRequest,
  CBTExamUpdateRequest,
  CBTExamItem,
  CBTExamsResponse,
  ConvertLeadPayload,
  ConvertLeadResponse,
  DashboardResponse,
  FeeStructuresResponse,
  ForgotPasswordPayload,
  FamilyDetail,
  FamiliesResponse,
  FinanceResponse,
  HelpdeskResponse,
  InvoiceDetail,
  LeadDetail,
  MessageTemplatesResponse,
  MessagingResponse,
  NotificationCreateRequest,
  NotificationItem,
  NotificationsResponse,
  ParentDetail,
  ParentsResponse,
  PasswordResetResponse,
  PINGenerateRequest,
  PINItem,
  PINsResponse,
  ReportsResponse,
  ResetPasswordPayload,
  SettingsResponse,
  StaffResponse,
  StudentCreateRequest,
  StudentDetail,
  StudentsResponse,
  TicketDetailResponse,
} from "@/types/crm";


const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach(callback => callback(token));
  refreshSubscribers = [];
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      throw new Error("Refresh failed");
    }

    const data = await response.json();
    if (data.access_token) {
      saveAuthTokens(data.access_token, data.refresh_token || refreshToken);
      if (data.user) {
        saveUser(data.user);
      }
      return data.access_token;
    }
    return null;
  } catch (error) {
    console.error("Token refresh failed:", error);
    clearAuthTokens();
    return null;
  }
}

async function request<T>(path: string, fallback: T, init?: RequestInit): Promise<T> {
  let accessToken = getAccessToken();
  
  const makeRequest = async (token: string | null): Promise<Response> => {
    return fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });
  };

  let response = await makeRequest(accessToken);

  if (response.status === 401 && accessToken) {
    if (!isRefreshing) {
      isRefreshing = true;
      const newToken = await refreshAccessToken();
      isRefreshing = false;
      
      if (newToken) {
        onTokenRefreshed(newToken);
        accessToken = newToken;
        response = await makeRequest(newToken);
      } else {
        // Refresh failed, clear tokens and redirect to login
        clearAuthTokens();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        throw new Error("Session expired");
      }
    } else {
      // Wait for refresh to complete
      return new Promise((resolve, reject) => {
        subscribeTokenRefresh((token: string) => {
          makeRequest(token)
            .then(res => {
              if (!res.ok) {
                reject(new Error(`Request failed with status ${res.status}`));
              } else {
                res.json().then(data => resolve(data as T));
              }
            })
            .catch(reject);
        });
      });
    }
  }

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export const apiClient = {
  async login(payload: AuthPayload) {
    // Use backend API for authentication
    const backendResponse = await request<AuthResponse>("/auth/login", {} as AuthResponse, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    // Save tokens and user info from backend response
    if (backendResponse.access_token) {
      saveAuthTokens(backendResponse.access_token, backendResponse.refresh_token || "");
    }
    saveUser(backendResponse.user);

    return backendResponse;
  },

  async signup(payload: { fullName: string; email: string; password: string }) {
    const backendResponse = await request<AuthResponse>("/auth/signup", {} as AuthResponse, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    // Save tokens and user info from backend response
    if (backendResponse.access_token) {
      saveAuthTokens(backendResponse.access_token, backendResponse.refresh_token || "");
    }
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
  createLead(payload: Record<string, unknown>) {
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
  updateStudent(studentId: string, payload: Record<string, unknown>) {
    return request<{ id: string }>(
      `/students/${studentId}`,
      {} as { id: string },
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
    );
  },
  deleteStudent(studentId: string) {
    return request<{ success: boolean }>(
      `/students/${studentId}`,
      {} as { success: boolean },
      {
        method: "DELETE",
      },
    );
  },
  updateTicket(ticketId: string, payload: Record<string, unknown>) {
    return request<{ id: string }>(
      `/tickets/${ticketId}`,
      {} as { id: string },
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
    );
  },
  createTicket(payload: Record<string, unknown>) {
    return request<{ id: string }>(
      "/tickets",
      {} as { id: string },
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  },
  deleteTicket(ticketId: string) {
    return request<{ success: boolean }>(
      `/tickets/${ticketId}`,
      {} as { success: boolean },
      {
        method: "DELETE",
      },
    );
  },
  importStudentsCSV(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const accessToken = getAccessToken();
    return fetch(`${API_URL}/students/import/csv`, {
      method: 'POST',
      headers: {
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: formData,
    }).then(async (response) => {
      if (!response.ok) {
        if (response.status === 401) {
          const newToken = await refreshAccessToken();
          if (newToken) {
            const retryResponse = await fetch(`${API_URL}/students/import/csv`, {
              method: 'POST',
              headers: {
                Authorization: `Bearer ${newToken}`,
              },
              body: formData,
            });
            if (retryResponse.ok) {
              return await retryResponse.json();
            }
          }
          clearAuthTokens();
          if (typeof window !== "undefined") {
            window.location.href = "/login";
          }
          throw new Error("Session expired");
        }
        throw new Error(`Request failed with status ${response.status}`);
      }
      return await response.json();
    });
  },
  createStudent(payload: StudentCreateRequest) {
    return request<{ id: string }>(
      "/students",
      {} as { id: string },
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  },
  getCbtExams() {
    return request<CBTExamsResponse>(
      "/cbt/exams",
      {} as CBTExamsResponse,
    );
  },
  createCbtExam(payload: CBTExamCreateRequest) {
    return request<CBTExamItem>(
      "/cbt/exams",
      {} as CBTExamItem,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  },
  updateCbtExam(examId: number, payload: CBTExamUpdateRequest) {
    return request<CBTExamItem>(
      `/cbt/exams/${examId}`,
      {} as CBTExamItem,
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
    );
  },
  deleteCbtExam(examId: number) {
    return request<{ success: boolean }>(
      `/cbt/exams/${examId}`,
      {} as { success: boolean },
      {
        method: "DELETE",
      },
    );
  },
  getNotifications() {
    return request<NotificationsResponse>(
      "/notifications",
      {} as NotificationsResponse,
    );
  },
  createNotification(payload: NotificationCreateRequest) {
    return request<NotificationItem>(
      "/notifications",
      {} as NotificationItem,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  },
  deleteNotification(notificationId: number) {
    return request<{ success: boolean }>(
      `/notifications/${notificationId}`,
      {} as { success: boolean },
      {
        method: "DELETE",
      },
    );
  },
  getPins() {
    return request<PINsResponse>(
      "/pins",
      {} as PINsResponse,
    );
  },
  generatePins(payload: PINGenerateRequest) {
    return request<PINsResponse>(
      "/pins/generate",
      {} as PINsResponse,
      {
        method: "POST",
        body: JSON.stringify(payload),
      },
    );
  },
  blockPin(pinId: number) {
    return request<{ success: boolean }>(
      `/pins/${pinId}/block`,
      {} as { success: boolean },
      {
        method: "POST",
      },
    );
  },
  deletePin(pinId: number) {
    return request<{ success: boolean }>(
      `/pins/${pinId}`,
      {} as { success: boolean },
      {
        method: "DELETE",
      },
    );
  },
  updateSettings(payload: Record<string, unknown>) {
    return request<{ success: boolean }>(
      "/settings",
      {} as { success: boolean },
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      },
    );
  },
};

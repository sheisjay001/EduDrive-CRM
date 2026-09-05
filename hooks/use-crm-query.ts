"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/services/api-client";

export function useDashboardQuery() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: () => apiClient.getDashboard(),
  });
}

export function useAdmissionsQuery() {
  return useQuery({
    queryKey: ["admissions"],
    queryFn: () => apiClient.getAdmissions(),
  });
}

export function useLeadQuery(leadId: string) {
  return useQuery({
    queryKey: ["lead", leadId],
    queryFn: () => apiClient.getLead(leadId),
    enabled: Boolean(leadId),
  });
}

export function useFamiliesQuery() {
  return useQuery({
    queryKey: ["families"],
    queryFn: () => apiClient.getFamilies(),
  });
}

export function useFamilyQuery(familyId: string) {
  return useQuery({
    queryKey: ["family", familyId],
    queryFn: () => apiClient.getFamily(familyId),
    enabled: Boolean(familyId),
  });
}

export function useParentsQuery() {
  return useQuery({
    queryKey: ["parents"],
    queryFn: () => apiClient.getParents(),
  });
}

export function useParentQuery(parentId: string) {
  return useQuery({
    queryKey: ["parent", parentId],
    queryFn: () => apiClient.getParent(parentId),
    enabled: Boolean(parentId),
  });
}

export function useStudentsQuery() {
  return useQuery({
    queryKey: ["students"],
    queryFn: () => apiClient.getStudents(),
  });
}

export function useStudentQuery(studentId: string) {
  return useQuery({
    queryKey: ["student", studentId],
    queryFn: () => apiClient.getStudent(studentId),
    enabled: Boolean(studentId),
  });
}

export function useFinanceQuery() {
  return useQuery({
    queryKey: ["finance"],
    queryFn: () => apiClient.getFinance(),
  });
}

export function useMessagingQuery() {
  return useQuery({
    queryKey: ["messaging"],
    queryFn: () => apiClient.getMessaging(),
  });
}

export function useMessageTemplatesQuery() {
  return useQuery({
    queryKey: ["messageTemplates"],
    queryFn: () => apiClient.getMessageTemplates(),
  });
}

export function useHelpdeskQuery() {
  return useQuery({
    queryKey: ["helpdesk"],
    queryFn: () => apiClient.getHelpdesk(),
  });
}

export function useTicketQuery(ticketId: string) {
  return useQuery({
    queryKey: ["ticket", ticketId],
    queryFn: () => apiClient.getTicket(ticketId),
    enabled: Boolean(ticketId),
  });
}

export function useInvoiceQuery(invoiceId: string) {
  return useQuery({
    queryKey: ["invoice", invoiceId],
    queryFn: () => apiClient.getInvoice(invoiceId),
    enabled: Boolean(invoiceId),
  });
}

export function useFeeStructuresQuery() {
  return useQuery({
    queryKey: ["feeStructures"],
    queryFn: () => apiClient.getFeeStructures(),
  });
}

export function useStaffQuery() {
  return useQuery({
    queryKey: ["staff"],
    queryFn: () => apiClient.getStaff(),
  });
}

export function useReportsQuery() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: () => apiClient.getReports(),
  });
}

export function useSettingsQuery() {
  return useQuery({
    queryKey: ["settings"],
    queryFn: () => apiClient.getSettings(),
  });
}

export function useCbtExamsQuery() {
  return useQuery({
    queryKey: ["cbtExams"],
    queryFn: () => apiClient.getCbtExams(),
  });
}

export function useNotificationsQuery() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: () => apiClient.getNotifications(),
  });
}

export function usePinsQuery() {
  return useQuery({
    queryKey: ["pins"],
    queryFn: () => apiClient.getPins(),
  });
}

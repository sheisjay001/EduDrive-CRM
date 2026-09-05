"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useFeeStructuresQuery, useFinanceQuery } from "@/hooks/use-crm-query";
import { Edit, Trash2, Save, X } from "lucide-react";
import { getUser, getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function FinancePage() {
  const { data, isLoading, refetch } = useFinanceQuery();
  const { data: feeData, isLoading: feeLoading } = useFeeStructuresQuery();
  const [editingInvoice, setEditingInvoice] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState({});

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "bursar"].includes(userRole);
  const canDelete = userRole === "school_admin";

  const handleEdit = (invoice: { id: string; student: string; term: string; amountDue: string; amountPaid: string; dueDate: string; status: string }) => {
    setEditingInvoice(invoice.id);
    setEditFormData({ amount_due: invoice.amountDue, status: invoice.status });
  };

  const handleSaveEdit = async (invoiceId: string) => {
    try {
      const response = await fetch(`${API_URL}/invoices/${invoiceId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${getAccessToken()}` },
        body: JSON.stringify(editFormData),
      });
      if (response.ok) { setEditingInvoice(null); refetch(); alert("Invoice updated"); }
    } catch { alert("Error updating invoice"); }
  };

  const handleCancelEdit = () => { setEditingInvoice(null); setEditFormData({}); };

  const handleDelete = async (invoiceId: string) => {
    if (!confirm("Delete this invoice?")) return;
    try {
      const response = await fetch(`${API_URL}/invoices/${invoiceId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${getAccessToken()}` },
      });
      if (response.ok) { refetch(); alert("Invoice deleted"); }
    } catch { alert("Error deleting invoice"); }
  };

  const kpis = [
    { label: "Total billed", value: data?.summary.totalBilled ?? "", change: "Term-wide billing volume", tone: "neutral" as const },
    { label: "Collected", value: data?.summary.totalCollected ?? "", change: "Includes online and offline", tone: "good" as const },
    { label: "Overdue", value: data?.summary.overdue ?? "", change: "Needs follow-up attention", tone: "warn" as const },
    { label: "Collection rate", value: data?.summary.collectionRate ?? "", change: "Recovery for current term", tone: "good" as const },
  ];

  return (
    <AppShell
      eyebrow="Finance Operations"
      title="Collections, invoices, and debt visibility"
      description="Give the bursary team one place to track term billing, payment status, debt aging, and the next best collection action."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="flex flex-wrap gap-3">
            <Button asChild variant="secondary">
              <Link href="/finance/payments">Payment desk</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/finance/debtors">Debtors dashboard</Link>
            </Button>
          </div>
          <KpiGrid items={kpis} />
          <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
            <DataTable
              title="Invoice desk"
              description="Recent invoices with payment posture and due-date context."
              columns={["Invoice", "Student", "Term", "Amount due", "Amount paid", "Due date", "Status", "Actions"]}
              rows={data.invoices.map((invoice) => [
                <Link key={`${invoice.id}-link`} href={`/finance/invoices/${invoice.id}`} className="font-medium text-[#d9a441] hover:underline">
                  {invoice.id}
                </Link>,
                invoice.student,
                invoice.term,
                editingInvoice === invoice.id ? (
                  <input type="text" defaultValue={invoice.amountDue} onChange={(e) => setEditFormData({ ...editFormData, amount_due: e.target.value })} className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white" />
                ) : (
                  invoice.amountDue
                ),
                invoice.amountPaid,
                invoice.dueDate,
                editingInvoice === invoice.id ? (
                  <input type="text" defaultValue={invoice.status} onChange={(e) => setEditFormData({ ...editFormData, status: e.target.value })} className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white" />
                ) : (
                  <Badge key={`${invoice.id}-status`} tone={invoice.status === "Paid" ? "good" : invoice.status === "Overdue" ? "danger" : "warn"}>
                    {invoice.status}
                  </Badge>
                ),
                <div key={`${invoice.id}-actions`} className="flex gap-2">
                  {editingInvoice === invoice.id ? (
                    <>
                      <Button size="sm" onClick={() => handleSaveEdit(invoice.id)} className="bg-green-600 text-white hover:bg-green-700"><Save className="h-4 w-4" /></Button>
                      <Button size="sm" onClick={handleCancelEdit} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><X className="h-4 w-4" /></Button>
                    </>
                  ) : (
                    <>
                      {canEdit && <Button size="sm" onClick={() => handleEdit(invoice)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><Edit className="h-4 w-4" /></Button>}
                      {canDelete && <Button size="sm" onClick={() => handleDelete(invoice.id)} variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10"><Trash2 className="h-4 w-4" /></Button>}
                    </>
                  )}
                </div>,
              ])}
            />
            <div className="space-y-6">
              <Card className="space-y-5">
                <SectionTitle title="Fee structure manager" description="Term-driven class fees, due dates, and optional charges for the bursary team." />
                {feeLoading || !feeData ? (
                  <LoadingPanel />
                ) : (
                  <div className="space-y-3">
                    {feeData.items.slice(0, 3).map((item) => (
                      <div key={item.id} className="rounded-[28px] border border-white/10 bg-white/5 p-5">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <p className="text-sm font-semibold text-white">{item.title}</p>
                            <p className="mt-1 text-sm text-[#9eb1cf]">{item.className} • {item.termName}</p>
                          </div>
                          <Badge tone="neutral">Due {item.dueDays} days</Badge>
                        </div>
                        <p className="mt-4 text-3xl font-serif text-[#f9d28a]">{item.amount}</p>
                      </div>
                    ))}
                    <div className="text-sm text-[#9eb1cf]">
                      <Link href="/finance/fee-structures" className="text-[#d9a441] underline">
                        View full fee structure manager
                      </Link>
                    </div>
                  </div>
                )}
              </Card>
              <Card className="space-y-5">
                <SectionTitle title="Debtor watchlist" description="Families who need immediate collections outreach or payment plan follow-up." />
                <div className="space-y-3">
                  {data.debtors.map((debtor) => (
                    <div key={debtor.student} className="rounded-[28px] border border-white/10 bg-white/5 p-5">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold text-white">{debtor.student}</p>
                          <p className="mt-1 text-sm text-[#9eb1cf]">{debtor.className}</p>
                        </div>
                        <Badge tone="danger">{debtor.aging}</Badge>
                      </div>
                      <p className="mt-4 font-serif text-3xl text-[#f9d28a]">{debtor.balance}</p>
                      <p className="mt-2 text-sm text-[#9eb1cf]">{debtor.lastContact}</p>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}

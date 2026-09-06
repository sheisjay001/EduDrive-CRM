"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, KpiGrid, SectionTitle } from "@/components/dashboard/ops-primitives";
import { CreditCard, FileText, CalendarDays, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { getAccessToken, getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Invoice {
  id: string;
  invoice_number: string;
  amount_due: number;
  amount_paid: number;
  status: string;
  due_date?: string;
  description?: string;
  student_name?: string;
}

interface Payment {
  id: string;
  amount: number;
  paid_at?: string;
  payment_method?: string;
  payment_reference?: string;
  description?: string;
}

export default function ParentFinancePage() {
  const [loading, setLoading] = useState(true);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    Promise.allSettled([
      fetch(`${API_URL}/parent/invoices`, { headers }).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/parent/payments`, { headers }).then(r => r.ok ? r.json() : null),
    ]).then(([iRes, pRes]) => {
      if (iRes.status === "fulfilled" && iRes.value) setInvoices(iRes.value.invoices || iRes.value || []);
      if (pRes.status === "fulfilled" && pRes.value) setPayments(pRes.value.payments || pRes.value || []);
    }).catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const totalOutstanding = invoices.reduce(
    (sum, inv) => sum + (Number(inv.amount_due) - Number(inv.amount_paid || 0)), 0
  );
  const totalPaid = payments.reduce((sum, p) => sum + Number(p.amount || 0), 0);
  const overdueCount = invoices.filter(i => i.status === "overdue" || i.status === "pending").length;

  return (
    <AppShell
      eyebrow="Parent Portal"
      title="Invoices & Payments"
      description="View your fee invoices, payment history, and manage school fee payments."
      allowedRoles={["parent"]}
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <>
          <KpiGrid items={[
            { label: "Total Paid", value: `₦${totalPaid.toLocaleString()}`, change: `${payments.length} payment(s)`, tone: "good" },
            { label: "Outstanding", value: `₦${totalOutstanding.toLocaleString()}`, change: `${overdueCount} invoice(s) pending`, tone: overdueCount > 0 ? "warn" : "good" },
            { label: "Total Invoices", value: String(invoices.length), change: "This term", tone: "neutral" },
            { label: "Payment Rate", value: invoices.length > 0 ? `${Math.round((totalPaid / (totalPaid + totalOutstanding)) * 100)}%` : "0%", change: "Completion rate", tone: "neutral" },
          ]} />

          <div className="grid gap-6 mt-6 xl:grid-cols-[1.1fr_0.9fr]">
            <Card className="p-6">
              <SectionTitle title="Recent Invoices" description="Your fee invoices and payment status" />
              <div className="space-y-3 mt-4">
                {invoices.length === 0 ? (
                  <p className="text-[#9eb1cf]">No invoices on record.</p>
                ) : invoices.map((inv) => (
                  <div key={inv.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-semibold text-white">#{inv.invoice_number}</p>
                      <Badge tone={inv.status === "paid" || inv.status === "settled" ? "good" : inv.status === "overdue" ? "danger" : "warn"}>
                        {inv.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-[#9eb1cf]">{inv.student_name || "Unknown student"}</p>
                    <div className="flex items-center justify-between mt-3">
                      <div>
                        <p className="text-xs text-[#9eb1cf]">Amount Due</p>
                        <p className="text-lg font-semibold text-white">₦{Number(inv.amount_due).toLocaleString()}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-[#9eb1cf]">Balance</p>
                        <p className="text-lg font-semibold text-[#f9d28a]">₦{(Number(inv.amount_due) - Number(inv.amount_paid || 0)).toLocaleString()}</p>
                      </div>
                    </div>
                    {inv.due_date && (
                      <div className="flex items-center gap-2 mt-2 text-sm text-[#9eb1cf]">
                        <CalendarDays className="h-4 w-4" />
                        Due: {inv.due_date}
                      </div>
                    )}
                    <Button className="w-full mt-4">
                      <CreditCard className="mr-2 h-4 w-4" />
                      Pay Now
                    </Button>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle title="Payment History" description="Your recent payment transactions" />
              <div className="space-y-3 mt-4">
                {payments.length === 0 ? (
                  <p className="text-[#9eb1cf]">No payments on record.</p>
                ) : payments.map((pay) => (
                  <div key={pay.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/20 text-green-400">
                          <CheckCircle className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="font-semibold text-white">Payment Received</p>
                          <p className="text-sm text-[#9eb1cf]">{pay.payment_method || "Bank Transfer"}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-green-400">₦{Number(pay.amount).toLocaleString()}</p>
                        {pay.paid_at && <p className="text-xs text-[#9eb1cf]">{pay.paid_at}</p>}
                      </div>
                    </div>
                    {pay.payment_reference && (
                      <div className="mt-2 text-sm text-[#9eb1cf]">
                        Reference: {pay.payment_reference}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <Card className="p-6 mt-6">
            <SectionTitle title="Payment Methods" description="Available payment options for school fees" />
            <div className="grid gap-4 md:grid-cols-3 mt-4">
              <Button variant="secondary" className="justify-start h-auto py-4">
                <CreditCard className="mr-3 h-5 w-5" />
                <div className="text-left">
                  <p className="font-semibold">Card Payment</p>
                  <p className="text-xs text-[#9eb1cf]">Pay with debit/credit card</p>
                </div>
              </Button>
              <Button variant="secondary" className="justify-start h-auto py-4">
                <FileText className="mr-3 h-5 w-5" />
                <div className="text-left">
                  <p className="font-semibold">Bank Transfer</p>
                  <p className="text-xs text-[#9eb1cf]">Direct bank deposit</p>
                </div>
              </Button>
              <Button variant="secondary" className="justify-start h-auto py-4">
                <Clock className="mr-3 h-5 w-5" />
                <div className="text-left">
                  <p className="font-semibold">Payment Plan</p>
                  <p className="text-xs text-[#9eb1cf]">Installment options</p>
                </div>
              </Button>
            </div>
          </Card>
        </>
      )}
    </AppShell>
  );
}

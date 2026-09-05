"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, KpiGrid, SectionTitle } from "@/components/dashboard/ops-primitives";
import {
  Users, CreditCard, FileText, MessageSquare, Ticket, Bus, BookOpen,
  CalendarDays, ChevronRight, Mail, AlertTriangle
} from "lucide-react";
import { getAccessToken, getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Child {
  id: string;
  full_name: string;
  class?: string;
  grade?: string;
  date_of_birth?: string;
  student_id?: string;
  admission_number?: string;
}

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

interface Message {
  id: string;
  subject?: string;
  body?: string;
  sent_at?: string;
  channel?: string;
}

export default function ParentDashboardPage() {
  const [loading, setLoading] = useState(true);
  const [children, setChildren] = useState<Child[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    Promise.allSettled([
      fetch(`${API_URL}/parent/children`, { headers }).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/parent/invoices`, { headers }).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/parent/payments`, { headers }).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/parent/communications`, { headers }).then(r => r.ok ? r.json() : null),
    ]).then(([cRes, iRes, pRes, mRes]) => {
      if (cRes.status === "fulfilled" && cRes.value) setChildren(cRes.value.children || cRes.value || []);
      if (iRes.status === "fulfilled" && iRes.value) setInvoices(iRes.value.invoices || iRes.value || []);
      if (pRes.status === "fulfilled" && pRes.value) setPayments(pRes.value.payments || pRes.value || []);
      if (mRes.status === "fulfilled" && mRes.value) setMessages(mRes.value.communications || mRes.value.messages || []);
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
      title="Family Dashboard"
      description="View your children's academic records, make fee payments, access support, and track transportation."
      allowedRoles={["parent"]}
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <>
          <KpiGrid items={[
            { label: "Children", value: String(children.length), change: "Ward(s) registered", tone: "good" },
            { label: "Total Paid", value: `₦${totalPaid.toLocaleString()}`, change: `${payments.length} payment(s)`, tone: "good" },
            { label: "Outstanding", value: `₦${totalOutstanding.toLocaleString()}`, change: `${overdueCount} invoice(s) pending`, tone: "warn" },
            { label: "Messages", value: String(messages.length), change: "From school admin", tone: "neutral" },
          ]} />

          <div className="grid gap-6 mt-6 xl:grid-cols-[1.1fr_0.9fr]">
            <Card className="p-6">
              <SectionTitle title="My Children" description="Wards linked to your account" />
              <div className="space-y-3 mt-4">
                {children.length === 0 ? (
                  <p className="text-[#9eb1cf]">No children linked to your account yet.</p>
                ) : children.map((child) => (
                  <div key={child.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#1c64f2]/20 text-[#7fa5ff]">
                        <Users className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-semibold text-white">{child.full_name}</p>
                        <p className="text-sm text-[#9eb1cf]">
                          {child.class || child.grade || child.admission_number || child.student_id || "No class assigned"}
                        </p>
                      </div>
                    </div>
                    <Button variant="secondary" size="sm">
                      <BookOpen className="mr-1 h-4 w-4" />
                      Details <ChevronRight className="ml-1 h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle title="Invoices & Payments" description="Recent fee activity" />
              <div className="space-y-3 mt-4">
                {invoices.length === 0 && payments.length === 0 ? (
                  <p className="text-[#9eb1cf]">No invoices or payments on record.</p>
                ) : (
                  <>
                    {invoices.slice(0, 3).map((inv) => (
                      <div key={inv.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                        <div>
                          <p className="font-semibold text-white">#{inv.invoice_number}</p>
                          <p className="text-sm text-[#9eb1cf]">
                            Balance: ₦{(Number(inv.amount_due) - Number(inv.amount_paid || 0)).toLocaleString()}
                          </p>
                        </div>
                        <Badge tone={inv.status === "paid" || inv.status === "settled" ? "good" : inv.status === "overdue" ? "warn" : "neutral"}>
                          {inv.status}
                        </Badge>
                      </div>
                    ))}
                    {payments.slice(0, 2).map((pay) => (
                      <div key={pay.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                        <div>
                          <p className="font-semibold text-white">Payment Received</p>
                          <p className="text-sm text-[#9eb1cf]">{pay.payment_method || "Bank"} • {pay.paid_at || ""}</p>
                        </div>
                        <Badge tone="good">₦{Number(pay.amount).toLocaleString()}</Badge>
                      </div>
                    ))}
                  </>
                )}
                <div className="flex gap-2 mt-4">
                  <Button className="w-full justify-center">
                    <CreditCard className="mr-2 h-4 w-4" />
                    Make a Payment
                  </Button>
                  <Button variant="secondary" className="w-full justify-center">
                    <FileText className="mr-2 h-4 w-4" />
                    View All Invoices
                  </Button>
                </div>
              </div>
            </Card>
          </div>

          <div className="grid gap-6 mt-6 lg:grid-cols-3">
            <Card className="p-6">
              <SectionTitle title="Quick Actions" description="Get things done quickly" />
              <div className="grid grid-cols-2 gap-3 mt-4">
                <Button variant="secondary" className="justify-start">
                  <Ticket className="mr-2 h-4 w-4" /> New Ticket
                </Button>
                <Button variant="secondary" className="justify-start">
                  <MessageSquare className="mr-2 h-4 w-4" /> Messages
                </Button>
                <Button variant="secondary" className="justify-start">
                  <Bus className="mr-2 h-4 w-4" /> Transport
                </Button>
                <Button variant="secondary" className="justify-start">
                  <CalendarDays className="mr-2 h-4 w-4" /> Calendar
                </Button>
                <Button variant="secondary" className="justify-start">
                  <Mail className="mr-2 h-4 w-4" /> Contact School
                </Button>
                <Button variant="secondary" className="justify-start">
                  <AlertTriangle className="mr-2 h-4 w-4" /> Report Issue
                </Button>
              </div>
            </Card>

            <Card className="p-6 lg:col-span-2">
              <SectionTitle title="Recent Messages" description="Communication from the school" />
              <div className="space-y-3 mt-4">
                {messages.length === 0 ? (
                  <p className="text-[#9eb1cf]">No messages yet.</p>
                ) : messages.slice(0, 4).map((msg) => (
                  <div key={msg.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-white">{msg.subject || "School Notice"}</p>
                      <span className="text-xs text-[#9eb1cf]">{msg.sent_at || ""}</span>
                    </div>
                    <p className="mt-1 text-sm text-[#c9d7ef] line-clamp-2">
                      {msg.body || "Content not available."}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}

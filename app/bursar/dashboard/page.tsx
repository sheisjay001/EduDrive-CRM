"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, SectionTitle } from "@/components/dashboard/ops-primitives";
import { CreditCard, TrendingUp, AlertCircle, Users, DollarSign, Calendar, FileText } from "lucide-react";

export default function BursarDashboardPage() {
  return (
    <AppShell
      eyebrow="Bursar Portal"
      title="Finance Dashboard"
      description="Track fee collections, payment status, debt aging, and financial operations."
      allowedRoles={["bursar"]}
    >
      <KpiGrid items={[
        { label: "Total Billed", value: "₦1.2M", change: "+18% this term", tone: "neutral" },
        { label: "Collected", value: "₦850K", change: "+12% vs last term", tone: "good" },
        { label: "Outstanding", value: "₦350K", change: "23 invoices pending", tone: "warn" },
        { label: "Collection Rate", value: "71%", change: "+5% improvement", tone: "good" },
      ]} />

      <div className="grid gap-6 mt-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="p-6">
          <SectionTitle title="Recent Collections" description="Latest payments received" />
          <div className="space-y-3 mt-4">
            {[
              { student: "John Doe", amount: "₦45,000", date: "Today", method: "Bank Transfer" },
              { student: "Jane Smith", amount: "₦45,000", date: "Yesterday", method: "Cash" },
              { student: "Michael Brown", amount: "₦45,000", date: "2 days ago", method: "POS" },
              { student: "Sarah Johnson", amount: "₦45,000", date: "3 days ago", method: "Bank Transfer" },
            ].map((payment, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/20 text-green-400">
                    <DollarSign className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{payment.student}</p>
                    <p className="text-sm text-[#9eb1cf]">{payment.method}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-white">{payment.amount}</p>
                  <p className="text-sm text-[#9eb1cf]">{payment.date}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Quick Actions" description="Common bursar tasks" />
          <div className="grid gap-3 mt-4">
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <CreditCard className="h-4 w-4" />
              Record Payment
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <FileText className="h-4 w-4" />
              Generate Invoice
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <AlertCircle className="h-4 w-4" />
              View Debtors
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Calendar className="h-4 w-4" />
              Payment Schedule
            </button>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 mt-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <SectionTitle title="Outstanding Balances" description="Students with pending payments" />
          <div className="space-y-3 mt-4">
            {[
              { student: "Emma Davis", class: "SS 1B", balance: "₦90,000", overdue: "30 days" },
              { student: "James Miller", class: "JSS 2A", balance: "₦45,000", overdue: "15 days" },
              { student: "Olivia Garcia", class: "SS 1A", balance: "₦135,000", overdue: "45 days" },
            ].map((debtor, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-500/15 text-red-400">
                    <AlertCircle className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-medium text-white">{debtor.student}</p>
                    <p className="text-sm text-[#9eb1cf]">{debtor.class}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-white">{debtor.balance}</p>
                  <Badge tone="warn">{debtor.overdue} overdue</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Collection Summary" description="This term's performance" />
          <div className="space-y-4 mt-4">
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-[#9eb1cf]">Total Expected</p>
                <p className="text-lg font-semibold text-white">₦1.2M</p>
              </div>
              <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                <div className="h-full rounded-full bg-[#d9a441]" style={{ width: "100%" }} />
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-[#9eb1cf]">Collected</p>
                <p className="text-lg font-semibold text-white">₦850K</p>
              </div>
              <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                <div className="h-full rounded-full bg-green-500" style={{ width: "71%" }} />
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-[#9eb1cf]">Outstanding</p>
                <p className="text-lg font-semibold text-white">₦350K</p>
              </div>
              <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                <div className="h-full rounded-full bg-red-500" style={{ width: "29%" }} />
              </div>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

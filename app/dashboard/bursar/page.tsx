"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, LoadingPanel, SectionTitle, TrendPanel } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery } from "@/hooks/use-crm-query";

export default function BursarDashboardPage() {
  const { data, isLoading } = useDashboardQuery();

  return (
    <AppShell
      eyebrow="Finance Dashboard"
      title="Fee Collections & Payments"
      description="Monitor invoice status, track payments, and manage school revenue operations."
      allowedRoles={["super_admin", "school_admin", "bursar"]}
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <KpiGrid items={[
            { label: "Total Revenue", value: "₦1.2M", change: "+18% this term", tone: "good" },
            { label: "Outstanding", value: "₦450K", change: "23 invoices pending", tone: "warn" },
            { label: "Collection Rate", value: "73%", change: "+5% vs last term", tone: "good" },
            { label: "Payments Today", value: "₦85K", change: "12 transactions", tone: "neutral" },
          ]} />
          
          <div className="grid gap-6 mt-6 xl:grid-cols-[1.2fr_0.8fr]">
            <Card className="p-6">
              <SectionTitle
                title="Recent Payments"
                description="Latest fee payments received"
              />
              <div className="space-y-3 mt-4">
                {[
                  { student: "Emeka Johnson", amount: "₦125,000", method: "Paystack", date: "2 hours ago" },
                  { student: "Fatima Ahmed", amount: "₦85,000", method: "Flutterwave", date: "4 hours ago" },
                  { student: "Chinedu Okafor", amount: "₦150,000", method: "Bank Transfer", date: "Yesterday" },
                  { student: "Grace Adebayo", amount: "₦95,000", method: "Paystack", date: "Yesterday" },
                  { student: "David Nnamdi", amount: "₦110,000", method: "Flutterwave", date: "2 days ago" },
                ].map((payment, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <p className="font-semibold text-white">{payment.student}</p>
                      <p className="text-sm text-[#9eb1cf]">{payment.method} • {payment.date}</p>
                    </div>
                    <Badge tone="good">{payment.amount}</Badge>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="Pending Invoices"
                description="Overdue and upcoming payments"
              />
              <div className="space-y-3 mt-4">
                {[
                  { student: "Tunde Bakare", amount: "₦150,000", due: "3 days overdue", class: "SS 2" },
                  { student: "Ngozi Eze", amount: "₦125,000", due: "Due tomorrow", class: "JSS 3" },
                  { student: "Ibrahim Yusuf", amount: "₦85,000", due: "Due in 5 days", class: "SS 1" },
                  { student: "Amaka Obi", amount: "₦95,000", due: "Due in 7 days", class: "JSS 1" },
                ].map((invoice, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <p className="font-semibold text-white">{invoice.student}</p>
                      <p className="text-sm text-[#9eb1cf]">{invoice.class} • {invoice.due}</p>
                    </div>
                    <Badge tone={invoice.due.includes("overdue") ? "warn" : "neutral"}>{invoice.amount}</Badge>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <TrendPanel
            title="Weekly Revenue Trend"
            description="Fee collection performance over the current term"
            data={data.revenueTrend}
            metric="+18% stronger than prior week"
          />

          <Card className="p-6 mt-6">
            <SectionTitle
              title="Payment Methods Breakdown"
              description="Revenue by payment channel"
            />
            <div className="grid gap-4 mt-4 md:grid-cols-3">
              <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-4">
                <p className="font-semibold text-green-400">Paystack</p>
                <p className="mt-2 font-serif text-2xl text-white">₦680K</p>
                <p className="mt-1 text-sm text-[#9eb1cf]">57% of total</p>
              </div>
              <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">
                <p className="font-semibold text-blue-400">Flutterwave</p>
                <p className="mt-2 font-serif text-2xl text-white">₦420K</p>
                <p className="mt-1 text-sm text-[#9eb1cf]">35% of total</p>
              </div>
              <div className="rounded-xl border border-purple-500/20 bg-purple-500/5 p-4">
                <p className="font-semibold text-purple-400">Bank Transfer</p>
                <p className="mt-2 font-serif text-2xl text-white">₦100K</p>
                <p className="mt-1 text-sm text-[#9eb1cf]">8% of total</p>
              </div>
            </div>
          </Card>
        </>
      )}
    </AppShell>
  );
}

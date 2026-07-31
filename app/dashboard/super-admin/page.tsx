"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery } from "@/hooks/use-crm-query";

export default function SuperAdminDashboardPage() {
  const { data, isLoading } = useDashboardQuery();

  return (
    <AppShell
      eyebrow="Super Admin Dashboard"
      title="Multi-School Overview"
      description="Manage all schools, system-wide operations, and platform administration."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <KpiGrid items={[
            { label: "Total Schools", value: "12", change: "+2 this month", tone: "good" },
            { label: "Total Students", value: "4,521", change: "+156 this term", tone: "good" },
            { label: "System Revenue", value: "₦2.4M", change: "+18% vs last term", tone: "good" },
            { label: "Active Users", value: "89", change: "All systems operational", tone: "neutral" },
          ]} />
          
          <div className="grid gap-6 mt-6">
            <Card className="p-6">
              <SectionTitle
                title="School Performance Overview"
                description="Key metrics across all managed schools"
              />
              <div className="grid gap-4 mt-4 md:grid-cols-3">
                {[
                  { name: "Greenfield College", students: 1250, revenue: "₦850K", status: "Excellent" },
                  { name: "Springfield Academy", students: 890, revenue: "₦620K", status: "Good" },
                  { name: "Riverside School", students: 650, revenue: "₦420K", status: "Needs Attention" },
                ].map((school) => (
                  <div key={school.name} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-white">{school.name}</p>
                      <Badge tone={school.status === "Excellent" ? "good" : school.status === "Good" ? "neutral" : "warn"}>
                        {school.status}
                      </Badge>
                    </div>
                    <div className="mt-3 space-y-2">
                      <p className="text-sm text-[#9eb1cf]">Students: {school.students}</p>
                      <p className="text-sm text-[#9eb1cf]">Revenue: {school.revenue}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="System Health"
                description="Platform-wide operational status"
              />
              <div className="grid gap-4 mt-4 md:grid-cols-2">
                <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-4">
                  <p className="font-semibold text-green-400">Authentication System</p>
                  <p className="mt-2 text-sm text-[#9eb1cf]">All services operational • 99.9% uptime</p>
                </div>
                <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-4">
                  <p className="font-semibold text-green-400">Database Cluster</p>
                  <p className="mt-2 text-sm text-[#9eb1cf]">Healthy • 0.3ms average latency</p>
                </div>
                <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-4">
                  <p className="font-semibold text-green-400">Payment Gateway</p>
                  <p className="mt-2 text-sm text-[#9eb1cf]">Paystack & Flutterwave active</p>
                </div>
                <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4">
                  <p className="font-semibold text-yellow-400">Email Service</p>
                  <p className="mt-2 text-sm text-[#9eb1cf]">Brevo SMTP • Rate limit: 28/hr remaining</p>
                </div>
              </div>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}

"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery } from "@/hooks/use-crm-query";

export default function HelpdeskDashboardPage() {
  const { data, isLoading } = useDashboardQuery();

  return (
    <AppShell
      eyebrow="Helpdesk Dashboard"
      title="Support & Ticket Management"
      description="Track parent inquiries, manage support tickets, and ensure timely resolution of issues."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <KpiGrid items={[
            { label: "Open Tickets", value: "12", change: "3 new today", tone: "neutral" },
            { label: "Resolved Today", value: "8", change: "+2 vs yesterday", tone: "good" },
            { label: "Avg Response", value: "2.5h", change: "-30min improvement", tone: "good" },
            { label: "Escalated", value: "2", change: "Requires attention", tone: "warn" },
          ]} />
          
          <div className="grid gap-6 mt-6 xl:grid-cols-[1.2fr_0.8fr]">
            <Card className="p-6">
              <SectionTitle
                title="Active Tickets"
                description="Open support tickets requiring attention"
              />
              <div className="space-y-3 mt-4">
                {[
                  { id: "TKT-001", parent: "Mrs. Johnson", subject: "Fee payment dispute", priority: "High", status: "Open", age: "2 hours" },
                  { id: "TKT-002", parent: "Mr. Ahmed", subject: "Transportation issue", priority: "Medium", status: "In Progress", age: "5 hours" },
                  { id: "TKT-003", parent: "Mrs. Okafor", subject: "Grade inquiry", priority: "Low", status: "Open", age: "1 day" },
                  { id: "TKT-004", parent: "Mr. Yusuf", subject: "Facility complaint", priority: "High", status: "Escalated", age: "3 hours" },
                  { id: "TKT-005", parent: "Mrs. Adebayo", subject: "Schedule change request", priority: "Medium", status: "Open", age: "6 hours" },
                ].map((ticket) => (
                  <div key={ticket.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-white">{ticket.id}</p>
                        <Badge tone={ticket.priority === "High" ? "warn" : ticket.priority === "Medium" ? "neutral" : "good"}>{ticket.priority}</Badge>
                      </div>
                      <p className="text-sm text-[#9eb1cf] mt-1">{ticket.parent} • {ticket.subject}</p>
                      <p className="text-xs text-[#9eb1cf] mt-1">{ticket.age} ago</p>
                    </div>
                    <Badge tone={ticket.status === "Escalated" ? "warn" : ticket.status === "In Progress" ? "good" : "neutral"}>{ticket.status}</Badge>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="Ticket Categories"
                description="Breakdown by issue type"
              />
              <div className="space-y-3 mt-4">
                {[
                  { category: "Fee & Payments", count: 5, percentage: "42%" },
                  { category: "Academic Issues", count: 3, percentage: "25%" },
                  { category: "Facilities", count: 2, percentage: "17%" },
                  { category: "Transportation", count: 1, percentage: "8%" },
                  { category: "Other", count: 1, percentage: "8%" },
                ].map((cat) => (
                  <div key={cat.category} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <p className="font-semibold text-white">{cat.category}</p>
                      <p className="text-sm text-[#9eb1cf]">{cat.percentage} of total</p>
                    </div>
                    <Badge tone="neutral">{cat.count} tickets</Badge>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <div className="grid gap-6 mt-6 xl:grid-cols-2">
            <Card className="p-6">
              <SectionTitle
                title="Recent Resolutions"
                description="Tickets resolved in the last 24 hours"
              />
              <div className="space-y-3 mt-4">
                {[
                  { id: "TKT-098", parent: "Mr. Nnamdi", issue: "Lost ID card", resolution: "Replacement issued", time: "2 hours ago" },
                  { id: "TKT-097", parent: "Mrs. Eze", issue: "Library access", resolution: "Access granted", time: "5 hours ago" },
                  { id: "TKT-096", parent: "Mr. Obi", issue: "Uniform inquiry", resolution: "Size provided", time: "8 hours ago" },
                  { id: "TKT-095", parent: "Mrs. Bakare", issue: "Cafeteria concern", resolution: "Menu updated", time: "12 hours ago" },
                ].map((resolved, idx) => (
                  <div key={idx} className="flex items-start gap-3 rounded-xl border border-green-500/20 bg-green-500/5 p-4">
                    <div className="w-2 h-2 mt-2 rounded-full bg-green-400" />
                    <div className="flex-1">
                      <p className="font-semibold text-white">{resolved.id} - {resolved.parent}</p>
                      <p className="text-sm text-[#9eb1cf]">{resolved.issue}</p>
                      <p className="text-sm text-green-400 mt-1">{resolved.resolution}</p>
                      <p className="text-xs text-[#9eb1cf] mt-1">{resolved.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="Performance Metrics"
                description="Helpdesk team performance this week"
              />
              <div className="grid gap-4 mt-4 md:grid-cols-2">
                <div className="rounded-xl border border-green-500/20 bg-green-500/5 p-4">
                  <p className="text-sm text-[#9eb1cf]">Resolution Rate</p>
                  <p className="mt-2 font-serif text-2xl text-white">87%</p>
                  <p className="mt-1 text-xs text-green-400">Above target</p>
                </div>
                <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">
                  <p className="text-sm text-[#9eb1cf]">Customer Satisfaction</p>
                  <p className="mt-2 font-serif text-2xl text-white">4.6/5</p>
                  <p className="mt-1 text-xs text-blue-400">Based on feedback</p>
                </div>
                <div className="rounded-xl border border-purple-500/20 bg-purple-500/5 p-4">
                  <p className="text-sm text-[#9eb1cf]">Avg Resolution Time</p>
                  <p className="mt-2 font-serif text-2xl text-white">4.2h</p>
                  <p className="mt-1 text-xs text-purple-400">-45min vs last week</p>
                </div>
                <div className="rounded-xl border border-orange-500/20 bg-orange-500/5 p-4">
                  <p className="text-sm text-[#9eb1cf]">First Response Time</p>
                  <p className="mt-2 font-serif text-2xl text-white">1.8h</p>
                  <p className="mt-1 text-xs text-orange-400">Within SLA</p>
                </div>
              </div>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}

"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, SectionTitle } from "@/components/dashboard/ops-primitives";
import { LifeBuoy, Ticket, Clock, CheckCircle, AlertCircle, MessageSquare, TrendingUp } from "lucide-react";

export default function HelpdeskOfficerDashboardPage() {
  return (
    <AppShell
      eyebrow="Help Desk Portal"
      title="Support Dashboard"
      description="Track support tickets, SLA compliance, and parent satisfaction."
      allowedRoles={["helpdesk_officer"]}
    >
      <KpiGrid items={[
        { label: "Open Tickets", value: "23", change: "+5 this week", tone: "warn" },
        { label: "Resolved Today", value: "12", change: "+3 vs yesterday", tone: "good" },
        { label: "SLA Compliance", value: "89%", change: "+2% improvement", tone: "good" },
        { label: "Avg Response", value: "2.5h", change: "-30min faster", tone: "good" },
      ]} />

      <div className="grid gap-6 mt-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="p-6">
          <SectionTitle title="Recent Tickets" description="Latest support requests" />
          <div className="space-y-3 mt-4">
            {[
              { id: "TKT-001", subject: "Fee payment issue", parent: "John Doe", priority: "High", status: "In Progress" },
              { id: "TKT-002", subject: "Transport inquiry", parent: "Jane Smith", priority: "Medium", status: "Open" },
              { id: "TKT-003", subject: "Academic concern", parent: "Michael Brown", priority: "Low", status: "Resolved" },
              { id: "TKT-004", subject: "Portal access", parent: "Sarah Johnson", priority: "Urgent", status: "In Progress" },
            ].map((ticket, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                    <Ticket className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{ticket.id}</p>
                    <p className="text-sm text-[#9eb1cf]">{ticket.subject}</p>
                    <p className="text-xs text-[#9eb1cf]">{ticket.parent}</p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge tone={ticket.priority === "Urgent" ? "danger" : ticket.priority === "High" ? "warn" : "neutral"}>
                    {ticket.priority}
                  </Badge>
                  <Badge tone={ticket.status === "Resolved" ? "good" : ticket.status === "In Progress" ? "warn" : "neutral"} className="ml-2">
                    {ticket.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Quick Actions" description="Common helpdesk tasks" />
          <div className="grid gap-3 mt-4">
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Ticket className="h-4 w-4" />
              Create Ticket
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <MessageSquare className="h-4 w-4" />
              Send Response
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Clock className="h-4 w-4" />
              View SLA Alerts
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <TrendingUp className="h-4 w-4" />
              View Analytics
            </button>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 mt-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <SectionTitle title="Ticket Status Overview" description="Tickets by status" />
          <div className="space-y-3 mt-4">
            {[
              { status: "Open", count: 8, color: "bg-blue-500" },
              { status: "In Progress", count: 10, color: "bg-yellow-500" },
              { status: "Pending", count: 5, color: "bg-orange-500" },
              { status: "Resolved", count: 45, color: "bg-green-500" },
              { status: "Closed", count: 32, color: "bg-gray-500" },
            ].map((status, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className={`h-3 w-3 rounded-full ${status.color}`} />
                  <p className="font-medium text-white">{status.status}</p>
                </div>
                <div className="flex items-center gap-4">
                  <p className="font-semibold text-white">{status.count} tickets</p>
                  <div className="h-2 w-24 rounded-full bg-white/10 overflow-hidden">
                    <div className={`h-full rounded-full ${status.color}`} style={{ width: `${(status.count / 45) * 100}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="SLA Alerts" description="Tickets approaching deadline" />
          <div className="space-y-3 mt-4">
            {[
              { id: "TKT-004", subject: "Portal access", timeLeft: "2 hours" },
              { id: "TKT-007", subject: "Grade inquiry", timeLeft: "4 hours" },
              { id: "TKT-012", subject: "Schedule change", timeLeft: "6 hours" },
            ].map((alert, idx) => (
              <div key={idx} className="flex items-center gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-500/20 text-red-400">
                  <AlertCircle className="h-4 w-4" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-white text-sm">{alert.id}</p>
                  <p className="text-xs text-[#9eb1cf]">{alert.subject}</p>
                </div>
                <p className="text-xs text-red-400 font-semibold">{alert.timeLeft}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

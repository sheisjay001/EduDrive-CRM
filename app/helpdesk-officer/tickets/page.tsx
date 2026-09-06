"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Ticket, Clock, User, Search, Filter, AlertCircle, CheckCircle, MessageSquare } from "lucide-react";

export default function HelpdeskOfficerTicketsPage() {
  return (
    <AppShell
      eyebrow="Help Desk Portal"
      title="Ticket Management"
      description="View and manage all support tickets."
      allowedRoles={["helpdesk_officer"]}
    >
      <Card className="p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9eb1cf]" />
            <input
              type="text"
              placeholder="Search tickets..."
              className="w-full rounded-lg border border-white/20 bg-white/10 pl-10 pr-4 py-2 text-sm text-white placeholder:text-[#9eb1cf] focus:border-[#d9a441] focus:outline-none"
            />
          </div>
          <button className="flex items-center gap-2 rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm text-white hover:bg-white/20">
            <Filter className="h-4 w-4" />
            Filter
          </button>
        </div>

        <div className="space-y-3">
          {[
            { id: "TKT-001", subject: "Fee payment issue", parent: "John Doe", priority: "High", status: "In Progress", created: "Sep 6, 2026", sla: "2 hours" },
            { id: "TKT-002", subject: "Transport inquiry", parent: "Jane Smith", priority: "Medium", status: "Open", created: "Sep 5, 2026", sla: "24 hours" },
            { id: "TKT-003", subject: "Academic concern", parent: "Michael Brown", priority: "Low", status: "Resolved", created: "Sep 4, 2026", sla: "48 hours" },
            { id: "TKT-004", subject: "Portal access", parent: "Sarah Johnson", priority: "Urgent", status: "In Progress", created: "Sep 3, 2026", sla: "1 hour" },
            { id: "TKT-005", subject: "Schedule change request", parent: "Emma Davis", priority: "Medium", status: "Open", created: "Sep 2, 2026", sla: "24 hours" },
          ].map((ticket, idx) => (
            <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                  <Ticket className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-semibold text-white">{ticket.id}</p>
                  <p className="text-sm text-white">{ticket.subject}</p>
                  <p className="text-xs text-[#9eb1cf] flex items-center gap-1 mt-1">
                    <User className="h-3 w-3" />
                    {ticket.parent}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="flex gap-2 justify-end">
                  <Badge tone={ticket.priority === "Urgent" ? "danger" : ticket.priority === "High" ? "warn" : "neutral"}>
                    {ticket.priority}
                  </Badge>
                  <Badge tone={ticket.status === "Resolved" ? "good" : ticket.status === "In Progress" ? "warn" : "neutral"}>
                    {ticket.status}
                  </Badge>
                </div>
                <p className="text-xs text-[#9eb1cf] mt-1 flex items-center gap-1 justify-end">
                  <Clock className="h-3 w-3" />
                  SLA: {ticket.sla}
                </p>
                <p className="text-xs text-[#9eb1cf]">{ticket.created}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </AppShell>
  );
}

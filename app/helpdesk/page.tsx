"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useHelpdeskQuery } from "@/hooks/use-crm-query";

export default function HelpdeskPage() {
  const { data, isLoading } = useHelpdeskQuery();

  return (
    <AppShell
      eyebrow="Help Desk"
      title="Keep complaints moving toward resolution"
      description="Track SLA pressure, assign the right internal owner, and give school leadership visibility into recurring parent pain points."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <DataTable
          title="Active complaint board"
          description="A practical queue for parent support, bursary issues, and school operations complaints."
          columns={["Ticket", "Subject", "Parent", "Priority", "Assignee", "SLA", "Status"]}
          rows={data.tickets.map((ticket) => [
            <Link key={`${ticket.id}-link`} href={`/helpdesk/${ticket.id}`} className="font-medium text-[#d9a441] hover:underline">
              {ticket.id}
            </Link>,
            ticket.subject,
            ticket.parent,
            <Badge key={`${ticket.id}-priority`} tone={ticket.priority === "Urgent" ? "danger" : ticket.priority === "High" ? "warn" : "neutral"}>
              {ticket.priority}
            </Badge>,
            ticket.assignee,
            ticket.sla,
            <Badge key={`${ticket.id}-status`} tone={ticket.status === "Resolved" ? "good" : "warn"}>
              {ticket.status}
            </Badge>,
          ])}
        />
      )}
    </AppShell>
  );
}

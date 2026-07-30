"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useTicketQuery } from "@/hooks/use-crm-query";

export default function TicketDetailPage() {
  const params = useParams();
  const ticketId = Array.isArray(params?.ticketId) ? params.ticketId[0] : params?.ticketId ?? "";
  const { data, isLoading } = useTicketQuery(ticketId);

  return (
    <AppShell
      eyebrow="Ticket detail"
      title="Help desk record"
      description="Review the ticket timeline, parent issue, and internal assignment details for follow-up."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <Card className="space-y-6">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Ticket</p>
              <p className="mt-3 text-3xl font-semibold text-white">{data.subject}</p>
              <div className="mt-3 flex flex-wrap gap-3">
                <Badge tone={data.priority === "Urgent" ? "danger" : data.priority === "High" ? "warn" : "neutral"}>
                  {data.priority}
                </Badge>
                <Badge tone={data.status === "Resolved" ? "good" : "warn"}>{data.status}</Badge>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[#9eb1cf]">Parent</p>
                <p className="mt-2 text-lg text-white">{data.parent}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Assigned to</p>
                <p className="mt-2 text-lg text-white">{data.assignee}</p>
              </div>
            </div>

            <div>
              <p className="text-sm text-[#9eb1cf]">Issue description</p>
              <p className="mt-3 rounded-[24px] border border-white/10 bg-white/5 p-5 text-sm leading-7 text-[#d6dfef]">
                {data.description}
              </p>
            </div>

            <div>
              <p className="text-sm text-[#9eb1cf]">Timeline</p>
              <div className="mt-4 space-y-3">
                {data.timeline.map((entry) => (
                  <div key={entry.time} className="rounded-[24px] border border-white/10 bg-white/5 p-4 text-sm text-[#d6dfef]">
                    <p className="font-semibold text-white">{entry.time}</p>
                    <p className="mt-1 leading-6">{entry.note}</p>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card className="space-y-4">
            <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Support context</p>
            <p className="text-sm leading-7 text-[#9eb1cf]">
              Use the timeline and assignment detail to close the ticket quickly and communicate status to the parent or internal team.
            </p>
            <div className="rounded-[24px] border border-white/10 bg-white/5 p-5 text-sm text-[#d6dfef]">
              <p className="text-white">Created at</p>
              <p className="mt-2">{data.createdAt}</p>
            </div>
            <div className="rounded-[24px] border border-white/10 bg-white/5 p-5 text-sm text-[#d6dfef]">
              <p className="text-white">SLA status</p>
              <p className="mt-2">{data.sla}</p>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}

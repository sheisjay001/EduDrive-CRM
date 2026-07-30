"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useLeadQuery } from "@/hooks/use-crm-query";

export default function LeadDetailPage() {
  const params = useParams();
  const leadId = Array.isArray(params?.leadId) ? params.leadId[0] : params?.leadId ?? "";
  const { data, isLoading } = useLeadQuery(leadId);

  return (
    <AppShell
      eyebrow="Admissions detail"
      title="Lead details"
      description="Review the lead context, contact profile, and next actions for conversion."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <Card className="space-y-5">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Lead ID</p>
              <p className="mt-2 text-2xl font-semibold text-white">{data.id}</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[#9eb1cf]">Child name</p>
                <p className="mt-2 text-lg text-white">{data.childName}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Parent</p>
                <p className="mt-2 text-lg text-white">{data.parentName}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Contact</p>
                <p className="mt-2 text-lg text-white">{data.parentEmail ?? "No email recorded"}</p>
                <p className="mt-1 text-sm text-[#9eb1cf]">{data.parentPhone ?? "No phone recorded"}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Source</p>
                <p className="mt-2 text-lg text-white">{data.source}</p>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-sm text-[#9eb1cf]">Stage</p>
                <Badge tone="neutral">{data.stage}</Badge>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Interested class</p>
                <p className="mt-2 text-lg text-white">{data.classInterest}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Next follow-up</p>
                <p className="mt-2 text-lg text-white">{data.followUp}</p>
              </div>
            </div>

            <div>
              <p className="text-sm text-[#9eb1cf]">Notes</p>
              <p className="mt-3 rounded-[24px] border border-white/10 bg-white/5 p-5 text-sm leading-7 text-[#d6dfef]">{data.notes}</p>
            </div>
          </Card>

          <Card className="space-y-4">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Admissions snapshot</p>
              <Badge tone="good">Created {data.createdAt}</Badge>
            </div>
            <p className="text-sm leading-7 text-[#9eb1cf]">
              Use this view to compare the lead’s stage and history before taking the next admission action.
            </p>
          </Card>
        </div>
      )}
    </AppShell>
  );
}

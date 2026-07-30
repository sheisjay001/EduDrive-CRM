"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useParentQuery } from "@/hooks/use-crm-query";

export default function ParentDetailPage() {
  const params = useParams();
  const parentId = Array.isArray(params?.parentId) ? params.parentId[0] : params?.parentId ?? "";
  const { data, isLoading } = useParentQuery(parentId);

  return (
    <AppShell
      eyebrow="Parent profile"
      title="Parent contact"
      description="Review guardian relationship, linked students, and communication preferences."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <Card className="space-y-5">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Contact</p>
              <p className="mt-2 text-2xl font-semibold text-white">{data.name}</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[#9eb1cf]">Relationship</p>
                <p className="mt-2 text-lg text-white">{data.relationship}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Preferred channel</p>
                <Badge tone="neutral">{data.preferredChannel}</Badge>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[#9eb1cf]">Phone</p>
                <p className="mt-2 text-lg text-white">{data.phone}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Email</p>
                <p className="mt-2 text-lg text-white">{data.email}</p>
              </div>
            </div>
            <div>
              <p className="text-sm text-[#9eb1cf]">Linked students</p>
              <div className="mt-3 space-y-2">
                {data.students.map((student) => (
                  <div key={student} className="rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-[#d6dfef]">
                    {student}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-sm text-[#9eb1cf]">Recent activity</p>
              <p className="mt-2 text-lg text-white">{data.lastActivity}</p>
            </div>
            <div>
              <p className="text-sm text-[#9eb1cf]">Notes</p>
              <p className="mt-3 rounded-[24px] border border-white/10 bg-white/5 p-5 text-sm leading-7 text-[#d6dfef]">{data.notes}</p>
            </div>
          </Card>

          <Card className="space-y-4">
            <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Engagement summary</p>
            <p className="text-sm leading-7 text-[#9eb1cf]">
              This page helps admissions, bursary, and support staff understand the parent’s communication preferences and linked student context before outreach.
            </p>
          </Card>
        </div>
      )}
    </AppShell>
  );
}

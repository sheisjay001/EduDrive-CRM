"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useFamilyQuery } from "@/hooks/use-crm-query";

export default function FamilyDetailPage() {
  const params = useParams();
  const familyId = Array.isArray(params?.familyId) ? params.familyId[0] : params?.familyId ?? "";
  const { data, isLoading } = useFamilyQuery(familyId);

  return (
    <AppShell
      eyebrow="Household detail"
      title="Family profile"
      description="Review household contacts, sibling grouping, and open operational actions."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <Card className="space-y-5">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Household</p>
              <p className="mt-2 text-2xl font-semibold text-white">{data.householdName}</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[#9eb1cf]">Guardians</p>
                <p className="mt-2 text-lg text-white">{data.guardians.join(", ")}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Students</p>
                <p className="mt-2 text-lg text-white">{data.students.join(", ")}</p>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-sm text-[#9eb1cf]">Balance</p>
                <p className="mt-2 text-lg text-white">{data.balance}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Status</p>
                <Badge tone={data.status === "Up to date" ? "good" : "warn"}>{data.status}</Badge>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Open tickets</p>
                <Badge tone={data.openTickets > 0 ? "danger" : "good"}>{data.openTickets}</Badge>
              </div>
            </div>
            <div>
              <p className="text-sm text-[#9eb1cf]">Last payment</p>
              <p className="mt-2 text-lg text-white">{data.lastPayment}</p>
            </div>
            <div>
              <p className="text-sm text-[#9eb1cf]">Notes</p>
              <p className="mt-3 rounded-[24px] border border-white/10 bg-white/5 p-5 text-sm leading-7 text-[#d6dfef]">{data.notes}</p>
            </div>
          </Card>

          <Card className="space-y-4">
            <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Family operations</p>
            <p className="text-sm leading-7 text-[#9eb1cf]">
              Use this record for billing follow-up, sibling communication, and to check whether any tickets are still open for the household.
            </p>
          </Card>
        </div>
      )}
    </AppShell>
  );
}

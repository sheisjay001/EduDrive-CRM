"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { ActionHint, InsightFeed, KpiGrid, LoadingPanel, SectionTitle, TrendPanel } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery } from "@/hooks/use-crm-query";

export default function DashboardPage() {
  const { data, isLoading } = useDashboardQuery();

  return (
    <AppShell
      eyebrow="Executive Dashboard"
      title="School command center"
      description="Track collections, admissions movement, complaints, and operational momentum for the current term from one place."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <KpiGrid items={data.kpis} />
          <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <Card className="space-y-5">
              <SectionTitle
                title="Admissions pipeline"
                description={`Current school: ${data.schoolName} • ${data.sessionLabel}`}
                action={<ActionHint text="Move directly into lead follow-up" />}
              />
              <div className="grid gap-4 md:grid-cols-2">
                {data.pipeline.map((stage) => (
                  <div key={stage.stage} className="rounded-[28px] border border-white/10 bg-white/5 p-5">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-lg font-semibold text-white">{stage.stage}</p>
                      <Badge tone="neutral">{stage.count} leads</Badge>
                    </div>
                    <p className="mt-4 font-serif text-4xl text-[#f9d28a]">{stage.value}</p>
                    <p className="mt-3 text-sm text-[#9eb1cf]">{stage.nextAction}</p>
                  </div>
                ))}
              </div>
            </Card>

            <InsightFeed items={data.activity} />
          </div>
          <TrendPanel
            title="Weekly collections pulse"
            description="A quick view of how fee recovery is moving through the week."
            data={data.revenueTrend}
            metric="+18% stronger than prior week"
          />
        </>
      )}
    </AppShell>
  );
}

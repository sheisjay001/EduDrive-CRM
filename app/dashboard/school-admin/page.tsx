"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, LoadingPanel, SectionTitle, TrendPanel } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery } from "@/hooks/use-crm-query";

export default function SchoolAdminDashboardPage() {
  const { data, isLoading } = useDashboardQuery();

  return (
    <AppShell
      eyebrow="School Admin Dashboard"
      title="School Command Center"
      description="Track collections, admissions movement, complaints, and operational momentum for the current term."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <KpiGrid items={data.kpis} />
          <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <Card className="space-y-5 p-6">
              <SectionTitle
                title="Admissions pipeline"
                description={`Current school: ${data.schoolName} • ${data.sessionLabel}`}
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

            <Card className="p-6">
              <SectionTitle
                title="Recent Activity"
                description="Latest actions across your school"
              />
              <div className="space-y-3 mt-4">
                {data.activity.slice(0, 5).map((item, idx) => (
                  <div key={idx} className="flex items-start gap-3 text-sm">
                    <div className="w-2 h-2 mt-2 rounded-full bg-blue-400" />
                    <div>
                      <p className="text-white">{item.title}</p>
                      <p className="text-[#9eb1cf]">{item.subtitle}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
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

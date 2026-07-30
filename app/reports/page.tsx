"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { LoadingPanel, TrendPanel } from "@/components/dashboard/ops-primitives";
import { useReportsQuery } from "@/hooks/use-crm-query";

export default function ReportsPage() {
  const { data, isLoading } = useReportsQuery();

  return (
    <AppShell
      eyebrow="Reporting"
      title="Analytics leaders can act on"
      description="Translate daily operations into conversion, collection, and engagement insights that leadership can use for planning and accountability."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="grid gap-4 xl:grid-cols-3">
            {data.cards.map((card) => (
              <Card key={card.title}>
                <p className="text-sm font-semibold text-white">{card.title}</p>
                <p className="mt-4 font-serif text-4xl text-[#f9d28a]">{card.value}</p>
                <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">{card.insight}</p>
              </Card>
            ))}
          </div>
          <div className="grid gap-6 xl:grid-cols-2">
            <TrendPanel
              title="Admissions trend"
              description="Monthly enrollment momentum for the current recruitment cycle."
              data={data.admissionsTrend}
              metric="Conversion improving"
            />
            <TrendPanel
              title="Collections trend"
              description="Weekly fee collection pattern across the current term."
              data={data.collectionsTrend}
              metric="Reminder strategy working"
            />
          </div>
        </>
      )}
    </AppShell>
  );
}

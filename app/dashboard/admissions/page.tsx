"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery } from "@/hooks/use-crm-query";

export default function AdmissionsDashboardPage() {
  const { data, isLoading } = useDashboardQuery();

  return (
    <AppShell
      eyebrow="Admissions Dashboard"
      title="Lead Management Center"
      description="Track prospective students, manage tours, and convert leads to enrollments."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <KpiGrid items={[
            { label: "Active Leads", value: "47", change: "+8 this week", tone: "good" },
            { label: "Tours Scheduled", value: "12", change: "3 today", tone: "neutral" },
            { label: "Conversions", value: "23", change: "+5 this month", tone: "good" },
            { label: "Response Rate", value: "78%", change: "+12% improvement", tone: "good" },
          ]} />
          
          <div className="grid gap-6 mt-6">
            <Card className="p-6">
              <SectionTitle
                title="Leads by Stage"
                description="Current pipeline status"
              />
              <div className="grid gap-4 mt-4 md:grid-cols-3">
                {data.pipeline.map((stage) => (
                  <div key={stage.stage} className="rounded-xl border border-white/10 bg-white/5 p-5">
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-white">{stage.stage}</p>
                      <Badge tone="neutral">{stage.count}</Badge>
                    </div>
                    <p className="mt-3 font-serif text-3xl text-[#f9d28a]">{stage.value}</p>
                    <p className="mt-2 text-sm text-[#9eb1cf]">{stage.nextAction}</p>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="Upcoming Tours"
                description="Scheduled school visits this week"
              />
              <div className="space-y-3 mt-4">
                {[
                  { name: "Johnson Family", date: "Today, 2:00 PM", interested: "JSS 1" },
                  { name: "Williams Family", date: "Tomorrow, 10:00 AM", interested: "SS 1" },
                  { name: "Adeyemi Family", date: "Wed, 3:30 PM", interested: "JSS 2" },
                ].map((tour, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <p className="font-semibold text-white">{tour.name}</p>
                      <p className="text-sm text-[#9eb1cf]">Interested in: {tour.interested}</p>
                    </div>
                    <Badge tone="neutral">{tour.date}</Badge>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="Recent Inquiries"
                description="Latest parent inquiries requiring follow-up"
              />
              <div className="space-y-3 mt-4">
                {data.activity.slice(0, 4).map((item, idx) => (
                  <div key={idx} className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="w-2 h-2 mt-2 rounded-full bg-orange-400" />
                    <div className="flex-1">
                      <p className="font-semibold text-white">{item.title}</p>
                      <p className="text-sm text-[#9eb1cf]">{item.subtitle}</p>
                    </div>
                    <Badge tone="warn">Follow-up</Badge>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}

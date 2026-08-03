"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useAdmissionsQuery } from "@/hooks/use-crm-query";
import type { KpiCard, LeadItem, StatusTone } from "@/types/crm";

type ScheduleRow = {
  id: string;
  activity: string;
  family: string;
  stage: string;
  slot: string;
  owner: string;
  tone: StatusTone;
};

function buildSchedule(leads: LeadItem[]): ScheduleRow[] {
  return leads.map((lead, index) => {
    if (lead.stage === "Tour Scheduled") {
      return {
        id: lead.id,
        activity: `Campus tour for ${lead.childName}`,
        family: lead.parentName,
        stage: lead.stage,
        slot: lead.followUp,
        owner: index % 2 === 0 ? "Admissions Desk" : "Front Desk",
        tone: "good" as const,
      };
    }

    if (lead.stage === "Assessment Booked") {
      return {
        id: lead.id,
        activity: `Assessment slot for ${lead.childName}`,
        family: lead.parentName,
        stage: lead.stage,
        slot: lead.followUp,
        owner: "Academic Team",
        tone: "warn" as const,
      };
    }

    return {
      id: lead.id,
      activity: `Follow-up with ${lead.parentName}`,
      family: lead.parentName,
      stage: lead.stage,
      slot: lead.followUp,
      owner: "Admissions Desk",
      tone: "neutral" as const,
    };
  });
}

export default function AdmissionsCalendarPage() {
  const { data, isLoading } = useAdmissionsQuery();

  if (isLoading || !data) {
    return (
      <AppShell
        eyebrow="Admissions Calendar"
        title="Tours, assessments, and follow-up slots"
        description="Keep visits, testing, and next-touch commitments organized in one schedule center."
      >
        <LoadingPanel />
      </AppShell>
    );
  }

  const schedule = buildSchedule(data.leads);
  const tours = schedule.filter((item) => item.stage === "Tour Scheduled").length;
  const assessments = schedule.filter((item) => item.stage === "Assessment Booked").length;
  const followUps = schedule.length - tours - assessments;

  const kpis: KpiCard[] = [
    { label: "Tours booked", value: String(tours), change: "Family visits on deck", tone: "good" },
    { label: "Assessments", value: String(assessments), change: "Academic screening slots", tone: "warn" },
    { label: "Follow-ups due", value: String(followUps), change: "Calls and reminders pending", tone: "neutral" },
    { label: "Schedule load", value: `${schedule.length}`, change: "Live admissions tasks", tone: "good" },
  ];

  return (
    <AppShell
      eyebrow="Admissions Calendar"
      title="Tours, assessments, and follow-up slots"
      description="Keep visits, testing, and next-touch commitments organized in one schedule center."
    >
      <div className="flex flex-wrap gap-3">
        <Button asChild variant="secondary">
          <Link href="/admissions">Back to pipeline</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/admissions?view=list">Open lead queue</Link>
        </Button>
      </div>

      <KpiGrid items={kpis} />

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <DataTable
          title="Schedule center"
          description="Daily visibility into tours, assessments, and outreach commitments tied to active leads."
          columns={["Lead", "Activity", "Family", "Stage", "Scheduled time", "Owner"]}
          rows={schedule.map((item) => [
            <Link key={`${item.id}-link`} href={`/admissions/leads/${item.id}`} className="font-medium text-[#d9a441] hover:underline">
              {item.id}
            </Link>,
            item.activity,
            item.family,
            <Badge key={`${item.id}-stage`} tone={item.tone}>
              {item.stage}
            </Badge>,
            item.slot,
            item.owner,
          ])}
        />

        <div className="space-y-6">
          <Card className="space-y-5">
            <SectionTitle
              title="Planning notes"
              description="Use the admissions stage to decide what belongs on the calendar and what just needs a quick same-day call."
            />
            <div className="space-y-3 text-sm leading-7 text-[#c1cee3]">
              <p>Tour-stage leads should leave the day with a confirmed arrival time, a named host, and a reminder message already prepared.</p>
              <p>Assessment-booked leads should carry the class interest, guardian contact, and any missing documents into the testing slot.</p>
              <p>Fresh and offered leads still need intentional follow-up blocks so nothing sits unowned between status changes.</p>
            </div>
          </Card>

          <Card className="space-y-4">
            <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Reminder ladder</p>
            <div className="space-y-3">
              {[
                "24 hours before: confirm date, time, and campus directions.",
                "2 hours before: send attendance nudge and host contact.",
                "Same day after visit: log outcome and next action before close of work.",
              ].map((item) => (
                <div key={item} className="rounded-[24px] border border-white/10 bg-white/5 p-4 text-sm text-[#d6dfef]">
                  {item}
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

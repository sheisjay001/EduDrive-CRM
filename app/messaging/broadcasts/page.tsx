"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useMessagingQuery } from "@/hooks/use-crm-query";
import type { KpiCard } from "@/types/crm";

export default function MessagingBroadcastsPage() {
  const { data, isLoading } = useMessagingQuery();

  if (isLoading || !data) {
    return (
      <AppShell
        eyebrow="Broadcast Center"
        title="Audience targeting and campaign delivery"
        description="Plan school-wide, finance, and admissions outreach by segment, channel mix, and send timing."
      >
        <LoadingPanel />
      </AppShell>
    );
  }

  const scheduledCount = data.campaigns.filter((campaign) => campaign.status === "Scheduled").length;
  const inProgressCount = data.campaigns.filter((campaign) => campaign.status === "In progress").length;

  const kpis: KpiCard[] = [
    { label: "Broadcasts", value: String(data.campaigns.length), change: "Live campaign rows", tone: "neutral" },
    { label: "Scheduled", value: String(scheduledCount), change: "Waiting on send window", tone: "warn" },
    { label: "In progress", value: String(inProgressCount), change: "Currently delivering", tone: "good" },
    { label: "Best reach", value: "WhatsApp", change: "Highest parent response channel", tone: "good" },
  ];

  return (
    <AppShell
      eyebrow="Broadcast Center"
      title="Audience targeting and campaign delivery"
      description="Plan school-wide, finance, and admissions outreach by segment, channel mix, and send timing."
    >
      <div className="flex flex-wrap gap-3">
        <Button asChild variant="secondary">
          <Link href="/messaging">Back to messaging overview</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/messaging/templates">Open template library</Link>
        </Button>
      </div>

      <KpiGrid items={kpis} />

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <DataTable
          title="Campaign queue"
          description="Operational broadcasts grouped by target audience, channel choice, and delivery posture."
          columns={["Title", "Audience", "Channel", "Status", "Scheduled / sent", "Playbook"]}
          rows={data.campaigns.map((campaign) => [
            campaign.title,
            campaign.audience,
            campaign.channel,
            <Badge key={`${campaign.title}-status`} tone={campaign.status === "Completed" ? "good" : campaign.status === "Scheduled" ? "warn" : "neutral"}>
              {campaign.status}
            </Badge>,
            campaign.sentAt,
            campaign.audience.includes("Debtors")
              ? "Pair with payment link and receipt reminder"
              : campaign.audience.includes("leads")
                ? "Include next step and admissions contact"
                : "Keep copy short and announcement-led",
          ])}
        />

        <div className="space-y-6">
          <Card className="space-y-5">
            <SectionTitle
              title="Audience builder"
              description="The PRD calls for segment-aware broadcasts. These are the highest-value slices already reflected in the product direction."
            />
            <div className="space-y-3">
              {[
                "Class-based notices for timetables, events, and academic updates.",
                "Debtor-status segments for reminders and payment-plan follow-up.",
                "Admissions-stage cohorts for tours, assessments, and offer nudges.",
                "Parent groups for school-wide announcements and help desk updates.",
              ].map((segment) => (
                <div key={segment} className="rounded-[24px] border border-white/10 bg-white/5 p-4 text-sm text-[#d6dfef]">
                  {segment}
                </div>
              ))}
            </div>
          </Card>

          <Card className="space-y-4">
            <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Channel mix</p>
            <div className="grid gap-3">
              {data.metrics.map((metric) => (
                <div key={metric.channel} className="rounded-[24px] border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-semibold text-white">{metric.channel}</p>
                    <Badge tone="good">{metric.delivery} delivered</Badge>
                  </div>
                  <p className="mt-2 text-sm text-[#9eb1cf]">Open / response signal: {metric.openRate}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

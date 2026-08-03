"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useMessagingQuery } from "@/hooks/use-crm-query";

export default function MessagingPage() {
  const { data, isLoading } = useMessagingQuery();

  return (
    <AppShell
      eyebrow="Messaging Hub"
      title="Reach parents on the right channel"
      description="Coordinate announcements, fee reminders, and operational messages across email, SMS, and WhatsApp with better audience targeting."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="flex flex-wrap gap-3">
            <Button asChild variant="secondary">
              <Link href="/messaging/broadcasts">Broadcast center</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/messaging/templates">Template library</Link>
            </Button>
          </div>
          <div className="grid gap-4 xl:grid-cols-3">
            {data.metrics.map((metric) => (
              <Card key={metric.channel}>
                <p className="text-sm font-semibold text-white">{metric.channel}</p>
                <p className="mt-4 font-serif text-4xl text-[#f9d28a]">{metric.sent}</p>
                <div className="mt-4 flex gap-2">
                  <Badge tone="good">Open: {metric.openRate}</Badge>
                  <Badge tone="neutral">Delivery: {metric.delivery}</Badge>
                </div>
              </Card>
            ))}
          </div>
          <DataTable
            title="Campaign timeline"
            description="Broadcasts, reminders, and parent-facing messages in the current operating window."
            columns={["Title", "Audience", "Channel", "Status", "Scheduled / Sent"]}
            rows={data.campaigns.map((campaign) => [
              campaign.title,
              campaign.audience,
              campaign.channel,
              <Badge key={`${campaign.title}-status`} tone={campaign.status === "Completed" ? "good" : campaign.status === "Scheduled" ? "warn" : "neutral"}>
                {campaign.status}
              </Badge>,
              campaign.sentAt,
            ])}
          />
          <Card>
            <SectionTitle title="Template strategy" description="Welcome, invoice, receipt, reminder, and complaint updates should all come from reusable message templates with role-safe sender identity." />
          </Card>
        </>
      )}
    </AppShell>
  );
}

"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useMessagingQuery } from "@/hooks/use-crm-query";
import { Bell, Plus, Trash2 } from "lucide-react";

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
            <Button className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
              <Bell className="mr-2 h-4 w-4" />
              Create Notification
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

          <Card className="p-6">
            <SectionTitle title="School Notifications" description="Create and manage targeted notifications for students, parents, and staff" />
            <div className="mt-4 space-y-3">
              {[
                { title: "Mid-term Examination Schedule", audience: "All Students", date: "Today", status: "sent" },
                { title: "Fee Payment Reminder", audience: "Parents with Outstanding Fees", date: "Yesterday", status: "sent" },
                { title: "Staff Meeting Notice", audience: "All Staff", date: "2 days ago", status: "sent" },
              ].map((notification, idx) => (
                <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-start gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/15 text-purple-400">
                      <Bell className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-semibold text-white">{notification.title}</p>
                      <p className="text-sm text-[#9eb1cf]">{notification.audience} • {notification.date}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge tone="good">{notification.status}</Badge>
                    <Button size="sm" variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </AppShell>
  );
}

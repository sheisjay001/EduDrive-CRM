"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useMessagingQuery, useNotificationsQuery } from "@/hooks/use-crm-query";
import { Bell, Plus, Trash2, X, Save } from "lucide-react";
import { apiClient } from "@/services/api-client";
import type { NotificationItem } from "@/types/crm";

export default function MessagingPage() {
  const { data, isLoading } = useMessagingQuery();
  const { data: notificationsData, isLoading: notificationsLoading, refetch: refetchNotifications } = useNotificationsQuery();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: "",
    message: "",
    target_audience: "all",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const notifications: NotificationItem[] = Array.isArray(notificationsData as unknown as NotificationItem[])
    ? (notificationsData as unknown as NotificationItem[])
    : (notificationsData as { notifications?: NotificationItem[] } | undefined)?.notifications ?? [];

  const handleCreateNotification = async () => {
    if (!createForm.title || !createForm.message) {
      alert("Title and message are required");
      return;
    }
    setIsSubmitting(true);
    try {
      await apiClient.createNotification({
        title: createForm.title,
        message: createForm.message,
        target_audience: createForm.target_audience,
      });
      alert("Notification created successfully");
      setShowCreateForm(false);
      setCreateForm({
        title: "",
        message: "",
        target_audience: "all",
      });
      await refetchNotifications();
    } catch (error) {
      alert("Error creating notification");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteNotification = async (id: number, title: string) => {
    if (!confirm(`Are you sure you want to delete notification "${title}"?`)) return;
    try {
      await apiClient.deleteNotification(id);
      alert("Notification deleted successfully");
      await refetchNotifications();
    } catch (error) {
      alert("Error deleting notification");
    }
  };

  const audienceLabels: Record<string, string> = {
    all: "All Users",
    student: "All Students",
    teacher: "All Teachers",
    parent: "All Parents",
    admin: "Administrators",
  };

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
            <Button onClick={() => setShowCreateForm(true)} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
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

            {showCreateForm && (
              <div className="mt-4 mb-5 rounded-[24px] border border-white/10 bg-white/5 p-5">
                <div className="mb-4 flex items-center justify-between">
                  <p className="text-lg font-semibold text-white">Create New Notification</p>
                  <Button size="sm" variant="outline" onClick={() => setShowCreateForm(false)} className="border-white/20 text-[#9eb1cf]">
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Title *</label>
                    <input
                      type="text"
                      value={createForm.title}
                      onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                      className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                      placeholder="Mid-term Examination Schedule"
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Audience</label>
                    <select
                      value={createForm.target_audience}
                      onChange={(e) => setCreateForm({ ...createForm, target_audience: e.target.value })}
                      className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                    >
                      <option value="all">All Users</option>
                      <option value="student">All Students</option>
                      <option value="teacher">All Teachers</option>
                      <option value="parent">All Parents</option>
                      <option value="admin">Administrators</option>
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Message *</label>
                    <textarea
                      value={createForm.message}
                      onChange={(e) => setCreateForm({ ...createForm, message: e.target.value })}
                      rows={4}
                      className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                      placeholder="The mid-term examination will begin on..."
                    />
                  </div>
                </div>
                <div className="mt-4 flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowCreateForm(false)} className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                    Cancel
                  </Button>
                  <Button onClick={handleCreateNotification} disabled={isSubmitting} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
                    <Save className="mr-2 h-4 w-4" />
                    {isSubmitting ? "Sending..." : "Send Notification"}
                  </Button>
                </div>
              </div>
            )}

            <div className="mt-4 space-y-3">
              {notificationsLoading ? (
                <p className="text-center text-[#9eb1cf]">Loading notifications…</p>
              ) : notifications.length === 0 ? (
                <p className="text-center text-[#9eb1cf]">No notifications yet — click "Create Notification" to send your first one.</p>
              ) : (
                notifications.map((notification) => (
                  <div key={notification.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-start gap-3 min-w-[240px] flex-1">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/15 text-purple-400 flex-shrink-0">
                        <Bell className="h-5 w-5" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-semibold text-white">{notification.title}</p>
                        <p className="mt-1 text-sm text-[#c1cee3]">{notification.message}</p>
                        <p className="mt-1 text-xs text-[#9eb1cf]">
                          {audienceLabels[notification.target_audience] ?? notification.target_audience}
                          {" • "}
                          {new Date(notification.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <Badge tone="good">sent</Badge>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDeleteNotification(notification.id, notification.title)}
                        className="border-red-500/30 text-red-500 hover:bg-red-500/10"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </>
      )}
    </AppShell>
  );
}

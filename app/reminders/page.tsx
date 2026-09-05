"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { Clock, Check, X, Plus } from "lucide-react";
import { getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Reminder {
  id: string;
  recipient: string;
  message: string;
  scheduled_for: string;
  status: string;
  reminder_type?: string;
  subject?: string;
  recipient_email?: string;
  recipient_phone?: string;
}

export default function RemindersPage() {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const fetchReminders = async () => {
    try {
      const response = await fetch(`${API_URL}/reminders/pending`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setReminders(Array.isArray(data) ? data : data.reminders || []);
      }
    } catch (error) {
      console.error("Error fetching reminders:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const loadReminders = async () => {
      await fetchReminders();
    };
    loadReminders();
  }, []);

  const handleSendReminder = async (reminderId: string) => {
    try {
      const response = await fetch(`${API_URL}/reminders/${reminderId}/send`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        fetchReminders();
      }
    } catch (error) {
      console.error("Error sending reminder:", error);
    }
  };

  const handleFailReminder = async (reminderId: string) => {
    try {
      const response = await fetch(`${API_URL}/reminders/${reminderId}/fail`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        fetchReminders();
      }
    } catch (error) {
      console.error("Error failing reminder:", error);
    }
  };

  const getReminderTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      lead_followup: "bg-blue-500/20 text-blue-400",
      payment_reminder: "bg-green-500/20 text-green-400",
      assessment: "bg-purple-500/20 text-purple-400",
      tour: "bg-yellow-500/20 text-yellow-400",
    };
    return colors[type] || "bg-gray-500/20 text-gray-400";
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: "bg-yellow-500/20 text-yellow-400",
      sent: "bg-green-500/20 text-green-400",
      failed: "bg-red-500/20 text-red-400",
    };
    return colors[status] || "bg-gray-500/20 text-gray-400";
  };

  return (
    <AppShell
      eyebrow="Reminders Management"
      title="Automated follow-ups and notifications"
      description="Manage automated reminders for leads, payments, assessments, and tours to ensure timely follow-ups."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button variant="secondary">
                <Clock className="mr-2 h-4 w-4" />
                Pending ({reminders.filter(r => r.status === 'pending').length})
              </Button>
              <Button variant="secondary">
                <Check className="mr-2 h-4 w-4" />
                Sent ({reminders.filter(r => r.status === 'sent').length})
              </Button>
              <Button variant="secondary">
                <X className="mr-2 h-4 w-4" />
                Failed ({reminders.filter(r => r.status === 'failed').length})
              </Button>
            </div>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Reminder
            </Button>
          </div>

          <Card className="p-6">
            <SectionTitle 
              title="Reminder Queue" 
              description="Pending and recent reminders" 
            />
            
            <div className="mt-6 space-y-4">
              {reminders.length === 0 ? (
                <p className="text-center text-[#9eb1cf]">No reminders found</p>
              ) : (
                reminders.map((reminder) => (
                  <div
                    key={reminder.id}
                    className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-4"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <Badge className={getReminderTypeColor(reminder.reminder_type || "general")}>
                          {reminder.reminder_type || "General"}
                        </Badge>
                        <Badge className={getStatusColor(reminder.status)}>
                          {reminder.status}
                        </Badge>
                        <span className="text-sm text-[#9eb1cf]">
                          Due: {new Date(reminder.scheduled_for).toLocaleString()}
                        </span>
                      </div>
                      <p className="mt-2 font-medium text-white">{reminder.subject}</p>
                      <p className="mt-1 text-sm text-[#9eb1cf]">{reminder.message}</p>
                      <p className="mt-1 text-xs text-[#8ea4c8]">
                        Recipient: {reminder.recipient_email || reminder.recipient_phone}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      {reminder.status === 'pending' && (
                        <>
                          <Button
                            size="sm"
                            onClick={() => handleSendReminder(reminder.id)}
                            className="bg-green-600 text-white hover:bg-green-700"
                          >
                            <Check className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => handleFailReminder(reminder.id)}
                            variant="outline"
                            className="border-red-500/30 text-red-500 hover:bg-red-500/10"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </>
                      )}
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

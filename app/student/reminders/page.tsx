"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Calendar, Clock, CheckCircle, AlertCircle, BookOpen, ClipboardList } from "lucide-react";
import { getAccessToken, getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Reminder {
  id: string;
  title: string;
  description?: string;
  due_date?: string;
  type: string;
  status: string;
}

interface ScheduleItem {
  id: string;
  subject?: string;
  day?: string;
  time?: string;
  room?: string;
}

export default function StudentRemindersPage() {
  const [loading, setLoading] = useState(true);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    Promise.allSettled([
      fetch(`${API_URL}/student/reminders`, { headers }).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/student/schedule`, { headers }).then(r => r.ok ? r.json() : null),
    ]).then(([rRes, sRes]) => {
      if (rRes.status === "fulfilled" && rRes.value) setReminders(rRes.value.reminders || rRes.value || []);
      if (sRes.status === "fulfilled" && sRes.value) setSchedule(sRes.value.schedule || sRes.value || []);
    }).catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell
      eyebrow="Student Portal"
      title="Schedule"
      description="View your class schedule, reminders, and upcoming events."
      allowedRoles={["student"]}
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Weekly Schedule</h3>
            {schedule.length === 0 ? (
              <p className="text-[#9eb1cf]">No schedule available.</p>
            ) : (
              <div className="space-y-3">
                {schedule.map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                        <BookOpen className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-semibold text-white">{item.subject || "Subject"}</p>
                        <p className="text-sm text-[#9eb1cf]">{item.day || "—"} • {item.room || "—"}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-white">{item.time || "—"}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Reminders</h3>
            {reminders.length === 0 ? (
              <p className="text-[#9eb1cf]">No reminders set.</p>
            ) : (
              <div className="space-y-3">
                {reminders.map((reminder) => (
                  <div key={reminder.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                          reminder.type === "assignment" ? "bg-purple-500/15 text-purple-400" :
                          reminder.type === "exam" ? "bg-red-500/15 text-red-400" :
                          "bg-blue-500/15 text-blue-400"
                        }`}>
                          {reminder.type === "assignment" ? <ClipboardList className="h-4 w-4" /> :
                           reminder.type === "exam" ? <AlertCircle className="h-4 w-4" /> :
                           <Calendar className="h-4 w-4" />}
                        </div>
                        <div>
                          <p className="font-semibold text-white">{reminder.title}</p>
                          {reminder.due_date && (
                            <p className="text-sm text-[#9eb1cf] flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {reminder.due_date}
                            </p>
                          )}
                        </div>
                      </div>
                      <Badge tone={reminder.status === "completed" ? "good" : reminder.status === "overdue" ? "warn" : "neutral"}>
                        {reminder.status}
                      </Badge>
                    </div>
                    {reminder.description && (
                      <p className="text-sm text-[#c9d7ef]">{reminder.description}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}
    </AppShell>
  );
}

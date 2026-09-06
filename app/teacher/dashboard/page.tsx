"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { KpiGrid, SectionTitle } from "@/components/dashboard/ops-primitives";
import { Users, CalendarCheck, BookOpen, MessageSquare, GraduationCap, TrendingUp, AlertCircle } from "lucide-react";

export default function TeacherDashboardPage() {
  return (
    <AppShell
      eyebrow="Teacher Portal"
      title="Classroom Management"
      description="Track student attendance, behavior, academic performance, and parent communications."
      allowedRoles={["teacher"]}
    >
      <KpiGrid items={[
        { label: "My Students", value: "45", change: "JSS 2A • SS 1B", tone: "neutral" },
        { label: "Attendance Today", value: "94%", change: "2 absent", tone: "good" },
        { label: "Pending Grades", value: "8", change: "Due this week", tone: "warn" },
        { label: "Parent Messages", value: "3", change: "Unread", tone: "neutral" },
      ]} />

      <div className="grid gap-6 mt-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="p-6">
          <SectionTitle title="Today's Schedule" description="Your classes for today" />
          <div className="space-y-3 mt-4">
            {[
              { time: "8:00 AM", subject: "Mathematics", class: "JSS 2A", room: "Room 12" },
              { time: "10:00 AM", subject: "Mathematics", class: "SS 1B", room: "Room 15" },
              { time: "1:00 PM", subject: "Basic Science", class: "JSS 2A", room: "Lab 3" },
            ].map((schedule, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                    <BookOpen className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{schedule.subject}</p>
                    <p className="text-sm text-[#9eb1cf]">{schedule.class} • {schedule.room}</p>
                  </div>
                </div>
                <Badge tone="neutral">{schedule.time}</Badge>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Quick Actions" description="Common teacher tasks" />
          <div className="grid grid-cols-2 gap-3 mt-4">
            <button className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:border-[#d9a441]/30 hover:bg-[#d9a441]/10">
              <CalendarCheck className="h-4 w-4" />
              Take Attendance
            </button>
            <button className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:border-[#d9a441]/30 hover:bg-[#d9a441]/10">
              <GraduationCap className="h-4 w-4" />
              Enter Grades
            </button>
            <button className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:border-[#d9a441]/30 hover:bg-[#d9a441]/10">
              <MessageSquare className="h-4 w-4" />
              Message Parents
            </button>
            <button className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:border-[#d9a441]/30 hover:bg-[#d9a441]/10">
              <AlertCircle className="h-4 w-4" />
              Report Issue
            </button>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 mt-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <SectionTitle title="Recent Student Activity" description="Latest updates from your classes" />
          <div className="space-y-3 mt-4">
            {[
              { student: "John Doe", action: "Submitted assignment", subject: "Mathematics", time: "2 hours ago" },
              { student: "Jane Smith", action: "Absent from class", subject: "Basic Science", time: "Today" },
              { student: "Michael Brown", action: "Grade improved", subject: "Mathematics", time: "Yesterday" },
            ].map((activity, idx) => (
              <div key={idx} className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/15 text-purple-400">
                  <Users className="h-4 w-4" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-white">{activity.student}</p>
                  <p className="text-sm text-[#9eb1cf]">{activity.action} • {activity.subject}</p>
                </div>
                <span className="text-xs text-[#9eb1cf]">{activity.time}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Performance Overview" description="Class statistics" />
          <div className="space-y-4 mt-4">
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-[#9eb1cf]">Average Attendance</p>
                <p className="text-lg font-semibold text-white">94%</p>
              </div>
              <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                <div className="h-full rounded-full bg-green-500" style={{ width: "94%" }} />
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-[#9eb1cf]">Assignment Completion</p>
                <p className="text-lg font-semibold text-white">87%</p>
              </div>
              <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                <div className="h-full rounded-full bg-[#d9a441]" style={{ width: "87%" }} />
              </div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-[#9eb1cf]">Class Average</p>
                <p className="text-lg font-semibold text-white">B+</p>
              </div>
              <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                <div className="h-full rounded-full bg-purple-500" style={{ width: "82%" }} />
              </div>
            </div>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

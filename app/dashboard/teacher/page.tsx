"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery } from "@/hooks/use-crm-query";
import { Upload, Users, CheckCircle, XCircle, User, BookOpen, Mail, Phone } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function TeacherDashboardPage() {
  const { data, isLoading } = useDashboardQuery();
  const [user, setUser] = useState<{ fullName?: string; email?: string; id?: string } | null>(null);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const stored = localStorage.getItem("user");
        if (stored) setUser(JSON.parse(stored));
      } catch { /* noop */ }
    };
    loadUser();
  }, []);

  return (
    <AppShell
      eyebrow="Teacher Dashboard"
      title="Classroom Management"
      description="Track student attendance, behavior, academic performance, and parent communications."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <Card className="p-6 mb-6">
            <SectionTitle title="My Profile" description="Your teacher information" />
            <div className="mt-4 flex items-start gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#d9a441]/15 text-[#d9a441]">
                <User className="h-8 w-8" />
              </div>
              <div className="flex-1 space-y-1">
                <p className="text-lg font-semibold text-white">{user?.fullName || "Teacher"}</p>
                <p className="text-sm text-[#9eb1cf]">{user?.email || "No email on record"}</p>
                <div className="pt-2 flex flex-wrap gap-2">
                  <Badge tone="good">Active</Badge>
                  <Badge tone="neutral">Mathematics & Physics</Badge>
                </div>
              </div>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[#8ea4c8]">
                  <BookOpen className="h-3 w-3" />
                  Subject
                </div>
                <p className="mt-1 font-medium text-white">Mathematics</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[#8ea4c8]">
                  <Mail className="h-3 w-3" />
                  Email
                </div>
                <p className="mt-1 font-medium text-white">{user?.email || "—"}</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-[#8ea4c8]">
                  <Phone className="h-3 w-3" />
                  Phone
                </div>
                <p className="mt-1 font-medium text-white">+234 800 000 0000</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                <p className="text-xs uppercase tracking-wider text-[#8ea4c8]">Classes</p>
                <p className="mt-1 font-medium text-white">JSS 2A • SS 1B</p>
              </div>
            </div>
          </Card>

          <KpiGrid items={[
            { label: "My Students", value: "45", change: "JSS 2A • SS 1B", tone: "neutral" },
            { label: "Attendance Today", value: "94%", change: "2 absent", tone: "good" },
            { label: "Pending Grades", value: "8", change: "Due this week", tone: "warn" },
            { label: "Parent Messages", value: "3", change: "Unread", tone: "neutral" },
          ]} />
          
          <div className="grid gap-6 mt-6 xl:grid-cols-[1.2fr_0.8fr]">
            <Card className="p-6">
              <SectionTitle
                title="Today's Attendance"
                description="Student presence for your classes"
              />
              <div className="space-y-3 mt-4">
                {[
                  { name: "JSS 2A - Mathematics", present: 28, absent: 2, total: 30 },
                  { name: "SS 1B - Physics", present: 25, absent: 0, total: 25 },
                  { name: "JSS 2A - Basic Science", present: 29, absent: 1, total: 30 },
                ].map((cls, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <p className="font-semibold text-white">{cls.name}</p>
                      <p className="text-sm text-[#9eb1cf]">{cls.present}/{cls.total} students present</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge tone="good">{cls.present} Present</Badge>
                      {cls.absent > 0 && <Badge tone="warn">{cls.absent} Absent</Badge>}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="Behavior Notes"
                description="Recent student behavior reports"
              />
              <div className="space-y-3 mt-4">
                {[
                  { student: "Chinedu Okafor", behavior: "Excellent participation", date: "Today", tone: "good" },
                  { student: "Ngozi Eze", behavior: "Late to class", date: "Today", tone: "warn" },
                  { student: "Emeka Johnson", behavior: "Helped classmates", date: "Yesterday", tone: "good" },
                  { student: "Fatima Ahmed", behavior: "Disruptive behavior", date: "Yesterday", tone: "warn" },
                ].map((note, idx) => (
                  <div key={idx} className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="w-2 h-2 mt-2 rounded-full bg-blue-400" />
                    <div className="flex-1">
                      <p className="font-semibold text-white">{note.student}</p>
                      <p className="text-sm text-[#9eb1cf]">{note.behavior}</p>
                      <p className="text-xs text-[#9eb1cf] mt-1">{note.date}</p>
                    </div>
                    <Badge tone={note.tone as "good" | "warn"}>{note.tone === "good" ? "Positive" : "Warning"}</Badge>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <div className="grid gap-6 mt-6 xl:grid-cols-2">
            <Card className="p-6">
              <SectionTitle
                title="Grade Submissions"
                description="Assignments and assessments pending grading"
              />
              <div className="space-y-3 mt-4">
                {[
                  { subject: "Mathematics - JSS 2A", assignment: "Mid-term Exam", due: "Tomorrow", count: 30 },
                  { subject: "Physics - SS 1B", assignment: "Lab Report", due: "In 3 days", count: 25 },
                  { subject: "Basic Science - JSS 2A", assignment: "Quiz Results", due: "In 5 days", count: 30 },
                ].map((task, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <p className="font-semibold text-white">{task.subject}</p>
                      <p className="text-sm text-[#9eb1cf]">{task.assignment}</p>
                    </div>
                    <div className="text-right">
                      <Badge tone={task.due === "Tomorrow" ? "warn" as const : "neutral" as const}>{task.due}</Badge>
                      <p className="text-xs text-[#9eb1cf] mt-1">{task.count} submissions</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="Parent Communications"
                description="Recent messages from parents"
              />
              <div className="space-y-3 mt-4">
                {[
                  { parent: "Mrs. Johnson", student: "Emeka Johnson", message: "Request for extra math support", date: "Today" },
                  { parent: "Mr. Ahmed", student: "Fatima Ahmed", message: "Question about physics project", date: "Yesterday" },
                  { parent: "Mrs. Okafor", student: "Chinedu Okafor", message: "Thank you for the feedback", date: "2 days ago" },
                ].map((msg, idx) => (
                  <div key={idx} className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="w-2 h-2 mt-2 rounded-full bg-purple-400" />
                    <div className="flex-1">
                      <p className="font-semibold text-white">{msg.parent} ({msg.student})</p>
                      <p className="text-sm text-[#9eb1cf]">{msg.message}</p>
                      <p className="text-xs text-[#9eb1cf] mt-1">{msg.date}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <div className="grid gap-6 mt-6 xl:grid-cols-2">
            <Card className="p-6">
              <SectionTitle
                title="My Students"
                description="Students assigned to your classes"
              />
              <div className="mt-4 space-y-3">
                {[
                  { name: "Chinedu Okafor", class: "JSS 2A", admission: "ADM-001" },
                  { name: "Ngozi Eze", class: "JSS 2A", admission: "ADM-002" },
                  { name: "Emeka Johnson", class: "SS 1B", admission: "ADM-003" },
                  { name: "Fatima Ahmed", class: "SS 1B", admission: "ADM-004" },
                ].map((student, idx) => (
                  <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500/15 text-blue-400">
                        <Users className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium text-white">{student.name}</p>
                        <p className="text-xs text-[#9eb1cf]">{student.class} • {student.admission}</p>
                      </div>
                    </div>
                    <Button size="sm" variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                      View
                    </Button>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="Attendance & Results Management"
                description="Mark attendance and upload student results"
              />
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <CheckCircle className="h-5 w-5 text-green-400" />
                    <p className="font-medium text-white">Mark Attendance</p>
                  </div>
                  <p className="text-sm text-[#9eb1cf] mb-3">Record daily attendance for your classes</p>
                  <Button variant="outline" className="w-full border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                    Open Attendance
                  </Button>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <Upload className="h-5 w-5 text-[#d9a441]" />
                    <p className="font-medium text-white">Upload Results</p>
                  </div>
                  <p className="text-sm text-[#9eb1cf] mb-3">Upload student results via CSV file</p>
                  <Button variant="outline" className="w-full border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                    Upload CSV
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}

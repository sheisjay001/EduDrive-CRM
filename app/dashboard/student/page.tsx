"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, KpiGrid, SectionTitle } from "@/components/dashboard/ops-primitives";
import {
  User, BookOpen, CalendarCheck, ClipboardList, AlertCircle,
  MessageSquare, Ticket, GraduationCap, Calendar, ChevronRight, Award, Clock
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface AttendanceDay {
  id?: string;
  date: string;
  status: string;
  notes?: string;
}

interface Assignment {
  id?: string;
  title: string;
  subject?: string;
  due_date?: string;
  status: string;
  grade?: string;
}

interface AcademicRecord {
  id?: string;
  subject?: string;
  grade?: string;
  score?: number;
  term?: string;
}

export default function StudentDashboardPage() {
  const [loading, setLoading] = useState(true);
  const [attendance, setAttendance] = useState<AttendanceDay[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [academic, setAcademic] = useState<AcademicRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<{ fullName?: string; email?: string; id?: string } | null>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("user");
      if (stored) setUser(JSON.parse(stored));
    } catch { /* noop */ }

    const token = localStorage.getItem("access_token");
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    Promise.allSettled([
      fetch(`${API_URL}/student/attendance`, { headers }).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/student/assignments`, { headers }).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/student/academic-records`, { headers }).then(r => r.ok ? r.json() : null),
    ]).then(([aRes, asRes, acRes]) => {
      if (aRes.status === "fulfilled" && aRes.value) setAttendance(aRes.value.attendance || aRes.value || []);
      if (asRes.status === "fulfilled" && asRes.value) setAssignments(asRes.value.assignments || asRes.value || []);
      if (acRes.status === "fulfilled" && acRes.value) setAcademic(acRes.value.academic_records || acRes.value.records || []);
    }).catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const presentDays = attendance.filter(a => a.status === "present").length;
  const totalDays = attendance.length || 1;
  const attendancePct = Math.round((presentDays / totalDays) * 100);
  const pendingAssignments = assignments.filter(a => a.status === "pending" || a.status === "in_progress").length;
  const overdueAssignments = assignments.filter(a => a.status === "overdue").length;
  const completedAssignments = assignments.filter(a => a.status === "completed").length;

  return (
    <AppShell
      eyebrow="Student Portal"
      title="My Academic Dashboard"
      description="Track attendance, assignments, grades, and school communication in one place."
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <>
          <KpiGrid items={[
            { label: "Attendance", value: `${attendancePct}%`, change: `${presentDays}/${totalDays} days present`, tone: attendancePct >= 80 ? "good" : attendancePct >= 60 ? "warn" : "warn" },
            { label: "Pending Work", value: String(pendingAssignments + overdueAssignments), change: `${overdueAssignments} overdue`, tone: overdueAssignments > 0 ? "warn" : "neutral" },
            { label: "Completed", value: String(completedAssignments), change: "Assignments submitted", tone: "good" },
            { label: "Subjects", value: String(academic.length || 6), change: "Registered subjects", tone: "neutral" },
          ]} />

          <div className="grid gap-6 mt-6 xl:grid-cols-[0.9fr_1.1fr]">
            <Card className="p-6">
              <SectionTitle title="My Profile" description="Your student information" />
              <div className="mt-4 flex items-start gap-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#1c64f2]/20 text-[#7fa5ff]">
                  <User className="h-7 w-7" />
                </div>
                <div className="flex-1 space-y-1">
                  <p className="text-lg font-semibold text-white">{user?.fullName || "Student"}</p>
                  <p className="text-sm text-[#9eb1cf]">{user?.email || "No email on record"}</p>
                  <div className="pt-2 flex flex-wrap gap-2">
                    <Badge tone="good">Enrolled</Badge>
                    <Badge tone="neutral">Full-time</Badge>
                  </div>
                </div>
              </div>
              <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                  <p className="text-xs uppercase tracking-wider text-[#8ea4c8]">Admission No</p>
                  <p className="mt-1 font-medium text-white">{user?.id?.slice(0, 8).toUpperCase() || "—"}</p>
                </div>
                <div className="rounded-lg border border-white/10 bg-white/5 p-3">
                  <p className="text-xs uppercase tracking-wider text-[#8ea4c8]">Academic Year</p>
                  <p className="mt-1 font-medium text-white">{new Date().getFullYear()}/{new Date().getFullYear() + 1}</p>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle title="Recent Attendance" description="Last 5 class days" />
              <div className="mt-4 space-y-2">
                {attendance.length === 0 ? (
                  <p className="text-[#9eb1cf]">No attendance records yet.</p>
                ) : (
                  attendance.slice(0, 5).map((day, idx) => (
                    <div key={day.id ?? idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-3">
                      <div className="flex items-center gap-3">
                        <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                          day.status === "present" ? "bg-green-500/15 text-green-400" :
                          day.status === "absent" ? "bg-red-500/15 text-red-400" :
                          day.status === "late" ? "bg-yellow-500/15 text-yellow-400" :
                          "bg-blue-500/15 text-blue-400"
                        }`}>
                          <CalendarCheck className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="font-medium text-white capitalize">{day.status}</p>
                          <p className="text-xs text-[#9eb1cf]">{day.date || "—"} {day.notes ? `• ${day.notes}` : ""}</p>
                        </div>
                      </div>
                      <Badge tone={
                        day.status === "present" ? "good" :
                        day.status === "absent" ? "warn" :
                        day.status === "late" ? "warn" : "neutral"
                      }>
                        {day.status}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>

          <div className="grid gap-6 mt-6 lg:grid-cols-3">
            <Card className="p-6 lg:col-span-2">
              <SectionTitle title="My Assignments" description="Homework, projects, and assessments" />
              <div className="mt-4 space-y-3">
                {assignments.length === 0 ? (
                  <p className="text-[#9eb1cf]">No assignments posted yet.</p>
                ) : (
                  assignments.slice(0, 5).map((a, idx) => (
                    <div key={a.id ?? idx} className="flex items-start justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="flex items-start gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/15 text-[#d9a441]">
                          <ClipboardList className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="font-semibold text-white">{a.title}</p>
                          <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-[#9eb1cf]">
                            <span className="flex items-center gap-1"><GraduationCap className="h-3 w-3" /> {a.subject || "General"}</span>
                            <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> Due: {a.due_date || "TBD"}</span>
                            {a.grade && <span className="flex items-center gap-1"><Award className="h-3 w-3" /> Grade: {a.grade}</span>}
                          </div>
                        </div>
                      </div>
                      <Badge tone={
                        a.status === "completed" ? "good" :
                        a.status === "overdue" ? "warn" :
                        a.status === "in_progress" ? "neutral" : "neutral"
                      }>
                        {a.status.replace("_", " ")}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle title="Quick Actions" description="Get things done quickly" />
              <div className="grid grid-cols-2 gap-3 mt-4">
                <Button variant="secondary" className="justify-start">
                  <BookOpen className="mr-2 h-4 w-4" /> Timetable
                </Button>
                <Button variant="secondary" className="justify-start">
                  <Calendar className="mr-2 h-4 w-4" /> Calendar
                </Button>
                <Button variant="secondary" className="justify-start">
                  <Ticket className="mr-2 h-4 w-4" /> Report Issue
                </Button>
                <Button variant="secondary" className="justify-start">
                  <MessageSquare className="mr-2 h-4 w-4" /> Messages
                </Button>
                <Button variant="secondary" className="justify-start">
                  <AlertCircle className="mr-2 h-4 w-4" /> Discipline
                </Button>
                <Button variant="secondary" className="justify-start">
                  <ChevronRight className="mr-2 h-4 w-4" /> More
                </Button>
              </div>
            </Card>
          </div>

          <div className="mt-6">
            <Card className="p-6">
              <SectionTitle title="Academic Summary" description="Subject performance snapshot" />
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {(academic.length > 0 ? academic : [
                  { subject: "Mathematics", grade: "B+", score: 82 },
                  { subject: "English Language", grade: "A-", score: 88 },
                  { subject: "Basic Science", grade: "B", grade2: "B", score: 76 },
                  { subject: "Social Studies", grade: "A", score: 91 },
                  { subject: "Agric Science", grade: "B+", score: 80 },
                  { subject: "Civic Education", grade: "A-", score: 85 },
                ] as AcademicRecord[]).map((rec, idx) => {
                  const score = rec.score ?? 0;
                  const tone = score >= 80 ? "good" : score >= 60 ? "neutral" : "warn";
                  return (
                    <div key={rec.id ?? idx} className="rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="flex items-center justify-between">
                        <p className="font-medium text-white">{rec.subject || `Subject ${idx + 1}`}</p>
                        <Badge tone={tone as "good" | "neutral" | "warn"}>{rec.grade || (score >= 80 ? "A" : score >= 60 ? "B" : "C")}</Badge>
                      </div>
                      <div className="mt-3 h-2 w-full rounded-full bg-white/10 overflow-hidden">
                        <div className={`h-full rounded-full ${score >= 80 ? "bg-green-500" : score >= 60 ? "bg-[#d9a441]" : "bg-red-500"}`} style={{ width: `${score || 70}%` }} />
                      </div>
                      <p className="mt-2 text-xs text-[#9eb1cf]">Score: {score || "—"}/100 {rec.term ? `• ${rec.term}` : ""}</p>
                    </div>
                  );
                })}
              </div>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}

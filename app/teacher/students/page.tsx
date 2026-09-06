"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Users, GraduationCap, CalendarCheck, BookOpen, TrendingUp, AlertCircle } from "lucide-react";

export default function TeacherStudentsPage() {
  return (
    <AppShell
      eyebrow="Teacher Portal"
      title="My Students"
      description="View and manage your assigned students, their attendance, and academic performance."
      allowedRoles={["teacher"]}
    >
      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">JSS 2A - Mathematics</h3>
          <div className="space-y-3">
            {[
              { name: "John Doe", attendance: "95%", grade: "A", status: "active" },
              { name: "Jane Smith", attendance: "88%", grade: "B+", status: "active" },
              { name: "Michael Brown", attendance: "92%", grade: "A-", status: "active" },
              { name: "Sarah Johnson", attendance: "78%", grade: "B", status: "warning" },
              { name: "David Wilson", attendance: "85%", grade: "B+", status: "active" },
            ].map((student, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                    <Users className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{student.name}</p>
                    <div className="flex items-center gap-3 mt-1 text-sm text-[#9eb1cf]">
                      <span className="flex items-center gap-1">
                        <CalendarCheck className="h-3 w-3" />
                        {student.attendance}
                      </span>
                      <span className="flex items-center gap-1">
                        <GraduationCap className="h-3 w-3" />
                        {student.grade}
                      </span>
                    </div>
                  </div>
                </div>
                <Badge tone={student.status === "active" ? "good" : "warn"}>
                  {student.status}
                </Badge>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">SS 1B - Mathematics</h3>
          <div className="space-y-3">
            {[
              { name: "Emma Davis", attendance: "98%", grade: "A+", status: "active" },
              { name: "James Miller", attendance: "90%", grade: "A", status: "active" },
              { name: "Olivia Garcia", attendance: "87%", grade: "A-", status: "active" },
              { name: "William Martinez", attendance: "82%", grade: "B+", status: "warning" },
            ].map((student, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/20 text-purple-400">
                    <Users className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{student.name}</p>
                    <div className="flex items-center gap-3 mt-1 text-sm text-[#9eb1cf]">
                      <span className="flex items-center gap-1">
                        <CalendarCheck className="h-3 w-3" />
                        {student.attendance}
                      </span>
                      <span className="flex items-center gap-1">
                        <GraduationCap className="h-3 w-3" />
                        {student.grade}
                      </span>
                    </div>
                  </div>
                </div>
                <Badge tone={student.status === "active" ? "good" : "warn"}>
                  {student.status}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

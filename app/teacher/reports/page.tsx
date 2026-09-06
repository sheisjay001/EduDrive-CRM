"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { FileText, GraduationCap, TrendingUp, Calendar, Download, BookOpen } from "lucide-react";

export default function TeacherReportsPage() {
  return (
    <AppShell
      eyebrow="Teacher Portal"
      title="Class Reports"
      description="View and generate academic reports for your classes."
      allowedRoles={["teacher"]}
    >
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                <GraduationCap className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs text-[#9eb1cf]">Total Students</p>
                <p className="text-2xl font-semibold text-white">45</p>
              </div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/20 text-green-400">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs text-[#9eb1cf]">Class Average</p>
                <p className="text-2xl font-semibold text-white">B+</p>
              </div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/20 text-purple-400">
                <FileText className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs text-[#9eb1cf]">Reports Generated</p>
                <p className="text-2xl font-semibold text-white">12</p>
              </div>
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Class Performance by Subject</h3>
          <div className="space-y-4">
            {[
              { subject: "Mathematics (JSS 2A)", average: "B+", students: 25, trend: "up" },
              { subject: "Mathematics (SS 1B)", average: "A-", students: 20, trend: "up" },
              { subject: "Basic Science (JSS 2A)", average: "B", students: 25, trend: "stable" },
            ].map((report, idx) => (
              <div key={idx} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                      <BookOpen className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-semibold text-white">{report.subject}</p>
                      <p className="text-sm text-[#9eb1cf]">{report.students} students</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge tone={
                      report.average.startsWith("A") ? "good" :
                      report.average.startsWith("B") ? "neutral" : "warn"
                    }>
                      {report.average}
                    </Badge>
                    <Badge tone={report.trend === "up" ? "good" : "neutral"}>
                      {report.trend === "up" ? "↑" : "→"}
                    </Badge>
                  </div>
                </div>
                <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      report.average.startsWith("A") ? "bg-green-500" :
                      report.average.startsWith("B") ? "bg-[#d9a441]" : "bg-red-500"
                    }`}
                    style={{ width: report.average.startsWith("A") ? "85%" : report.average.startsWith("B") ? "75%" : "60%" }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Generate Reports</h3>
          <div className="grid gap-3 md:grid-cols-2">
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Download className="h-4 w-4" />
              Download Class Report
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Download className="h-4 w-4" />
              Download Individual Reports
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Calendar className="h-4 w-4" />
              Generate Term Report
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <FileText className="h-4 w-4" />
              Generate Attendance Report
            </button>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

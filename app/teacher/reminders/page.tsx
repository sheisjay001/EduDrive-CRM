"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Calendar, Clock, CheckCircle, AlertCircle, BookOpen, ClipboardList, Plus } from "lucide-react";

export default function TeacherRemindersPage() {
  return (
    <AppShell
      eyebrow="Teacher Portal"
      title="Schedule & Reminders"
      description="View your class schedule, upcoming events, and important reminders."
      allowedRoles={["teacher"]}
    >
      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Weekly Schedule</h3>
          <div className="space-y-3">
            {[
              { day: "Monday", classes: ["Mathematics (JSS 2A) 8:00 AM", "Mathematics (SS 1B) 10:00 AM", "Basic Science (JSS 2A) 1:00 PM"] },
              { day: "Tuesday", classes: ["Mathematics (JSS 2A) 8:00 AM", "Mathematics (SS 1B) 10:00 AM", "Free Period 1:00 PM"] },
              { day: "Wednesday", classes: ["Mathematics (JSS 2A) 8:00 AM", "Staff Meeting 10:00 AM", "Basic Science (JSS 2A) 1:00 PM"] },
              { day: "Thursday", classes: ["Mathematics (JSS 2A) 8:00 AM", "Mathematics (SS 1B) 10:00 AM", "Basic Science (JSS 2A) 1:00 PM"] },
              { day: "Friday", classes: ["Mathematics (JSS 2A) 8:00 AM", "Mathematics (SS 1B) 10:00 AM", "Club Activity 1:00 PM"] },
            ].map((schedule, idx) => (
              <div key={idx} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                    <Calendar className="h-4 w-4" />
                  </div>
                  <p className="font-semibold text-white">{schedule.day}</p>
                </div>
                <div className="space-y-2 ml-11">
                  {schedule.classes.map((cls, cIdx) => (
                    <div key={cIdx} className="text-sm text-[#c9d7ef]">{cls}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Upcoming Tasks</h3>
            <button className="flex items-center gap-2 rounded-lg border border-[#d9a441]/30 bg-[#d9a441]/10 px-3 py-1.5 text-sm text-white transition-all hover:bg-[#d9a441]/20">
              <Plus className="h-4 w-4" />
              Add Task
            </button>
          </div>
          <div className="space-y-3">
            {[
              { title: "Grade Mathematics assignments", due: "Today", priority: "high", type: "grading" },
              { title: "Submit attendance report", due: "Tomorrow", priority: "medium", type: "admin" },
              { title: "Parent meeting - John Doe", due: "Sep 8", priority: "high", type: "meeting" },
              { title: "Prepare lesson plan for next week", due: "Sep 9", priority: "medium", type: "planning" },
              { title: "Review student progress reports", due: "Sep 10", priority: "low", type: "review" },
            ].map((task, idx) => (
              <div key={idx} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                      task.type === "grading" ? "bg-purple-500/15 text-purple-400" :
                      task.type === "meeting" ? "bg-red-500/15 text-red-400" :
                      task.type === "admin" ? "bg-blue-500/15 text-blue-400" :
                      "bg-green-500/15 text-green-400"
                    }`}>
                      {task.type === "grading" ? <ClipboardList className="h-4 w-4" /> :
                       task.type === "meeting" ? <AlertCircle className="h-4 w-4" /> :
                       task.type === "admin" ? <BookOpen className="h-4 w-4" /> :
                       <CheckCircle className="h-4 w-4" />}
                    </div>
                    <div>
                      <p className="font-semibold text-white">{task.title}</p>
                      <p className="text-sm text-[#9eb1cf] flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        Due: {task.due}
                      </p>
                    </div>
                  </div>
                  <Badge tone={task.priority === "high" ? "danger" : task.priority === "medium" ? "warn" : "neutral"}>
                    {task.priority}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Important Dates</h3>
          <div className="grid gap-3 md:grid-cols-2">
            {[
              { event: "Mid-term Examinations", date: "Sep 15 - Sep 20", type: "exam" },
              { event: "Parent-Teacher Conference", date: "Sep 25", type: "meeting" },
              { event: "Term End", date: "Oct 15", type: "academic" },
              { event: "Report Card Distribution", date: "Oct 20", type: "academic" },
            ].map((date, idx) => (
              <div key={idx} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                    date.type === "exam" ? "bg-red-500/15 text-red-400" :
                    date.type === "meeting" ? "bg-purple-500/15 text-purple-400" :
                    "bg-[#d9a441]/15 text-[#d9a441]"
                  }`}>
                    <Calendar className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-medium text-white">{date.event}</p>
                    <p className="text-sm text-[#9eb1cf]">{date.date}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

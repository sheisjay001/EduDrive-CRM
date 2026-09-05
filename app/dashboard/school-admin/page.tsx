"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, LoadingPanel, SectionTitle, TrendPanel } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery } from "@/hooks/use-crm-query";
import { Plus, Play, Edit, Trash2, Clock } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface CBTExam {
  id: number;
  title: string;
  student_class: string;
  duration_minutes: number;
  status: string;
  created_at: string;
}

export default function SchoolAdminDashboardPage() {
  const { data, isLoading } = useDashboardQuery();
  const [exams, setExams] = useState<CBTExam[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  useEffect(() => {
    fetchExams();
  }, []);

  const fetchExams = async () => {
    try {
      const response = await fetch(`${API_URL}/cbt/exams`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setExams(data.exams || []);
      }
    } catch (error) {
      console.error("Error fetching exams:", error);
    }
  };

  return (
    <AppShell
      eyebrow="School Admin Dashboard"
      title="School Command Center"
      description="Track collections, admissions movement, complaints, and operational momentum for the current term."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <KpiGrid items={data.kpis} />
          <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
            <Card className="space-y-5 p-6">
              <SectionTitle
                title="Admissions pipeline"
                description={`Current school: ${data.schoolName} • ${data.sessionLabel}`}
              />
              <div className="grid gap-4 md:grid-cols-2">
                {data.pipeline.map((stage) => (
                  <div key={stage.stage} className="rounded-[28px] border border-white/10 bg-white/5 p-5">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-lg font-semibold text-white">{stage.stage}</p>
                      <Badge tone="neutral">{stage.count} leads</Badge>
                    </div>
                    <p className="mt-4 font-serif text-4xl text-[#f9d28a]">{stage.value}</p>
                    <p className="mt-3 text-sm text-[#9eb1cf]">{stage.nextAction}</p>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle
                title="Recent Activity"
                description="Latest actions across your school"
              />
              <div className="space-y-3 mt-4">
                {data.activity.slice(0, 5).map((item, idx) => (
                  <div key={idx} className="flex items-start gap-3 text-sm">
                    <div className="w-2 h-2 mt-2 rounded-full bg-blue-400" />
                    <div>
                      <p className="text-white">{item.title}</p>
                      <p className="text-[#9eb1cf]">{item.subtitle}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
          <TrendPanel
            title="Weekly collections pulse"
            description="A quick view of how fee recovery is moving through the week."
            data={data.revenueTrend}
            metric="+18% stronger than prior week"
          />

          <Card className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <SectionTitle title="CBT Exams" description="Manage computer-based tests for students" />
              <Button onClick={() => setShowCreateDialog(true)} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
                <Plus className="mr-2 h-4 w-4" />
                Create Exam
              </Button>
            </div>
            <div className="space-y-3">
              {exams.length === 0 ? (
                <p className="text-center text-[#9eb1cf]">No CBT exams created yet</p>
              ) : (
                exams.map((exam) => (
                  <div key={exam.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-sm font-semibold text-white">{exam.title}</h3>
                        <Badge tone={exam.status === "active" ? "good" : "warn"}>
                          {exam.status}
                        </Badge>
                      </div>
                      <div className="mt-1 flex items-center gap-3 text-xs text-[#9eb1cf]">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {exam.duration_minutes} min
                        </span>
                        <span>{exam.student_class}</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button size="sm" variant="outline" className="border-green-500/30 text-green-500 hover:bg-green-500/10">
                        <Play className="h-3 w-3" />
                      </Button>
                      <Button size="sm" variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
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

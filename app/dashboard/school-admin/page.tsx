"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, LoadingPanel, SectionTitle, TrendPanel } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery, useCbtExamsQuery } from "@/hooks/use-crm-query";
import { Plus, Play, Edit, Trash2, Clock, Save, X } from "lucide-react";
import { apiClient } from "@/services/api-client";
import type { CBTExamItem } from "@/types/crm";

export default function SchoolAdminDashboardPage() {
  const { data, isLoading } = useDashboardQuery();
  const { data: examsData, isLoading: examsLoading, refetch: refetchExams } = useCbtExamsQuery();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingExamId, setEditingExamId] = useState<number | null>(null);
  const [editFormData, setEditFormData] = useState<Record<string, string | number>>({});
  const [createForm, setCreateForm] = useState({
    title: "",
    student_class: "",
    duration_minutes: 30,
    status: "active",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const exams: CBTExamItem[] = Array.isArray(examsData as unknown as CBTExamItem[])
    ? (examsData as unknown as CBTExamItem[])
    : (examsData as { exams?: CBTExamItem[] } | undefined)?.exams ?? [];

  const handleCreateExam = async () => {
    if (!createForm.title || !createForm.student_class) {
      alert("Title and class are required");
      return;
    }
    setIsSubmitting(true);
    try {
      await apiClient.createCbtExam({
        title: createForm.title,
        student_class: createForm.student_class,
        duration_minutes: Number(createForm.duration_minutes) || 30,
        status: createForm.status,
      });
      alert("Exam created successfully");
      setShowCreateForm(false);
      setCreateForm({
        title: "",
        student_class: "",
        duration_minutes: 30,
        status: "active",
      });
      await refetchExams();
    } catch (error) {
      alert("Error creating exam");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditExam = (exam: CBTExamItem) => {
    setEditingExamId(exam.id);
    setEditFormData({
      title: exam.title,
      student_class: exam.student_class,
      duration_minutes: exam.duration_minutes,
      status: exam.status,
    });
  };

  const handleSaveEdit = async (examId: number) => {
    try {
      await apiClient.updateCbtExam(examId, {
        title: String(editFormData.title ?? ""),
        student_class: String(editFormData.student_class ?? ""),
        duration_minutes: Number(editFormData.duration_minutes) || undefined,
        status: String(editFormData.status ?? ""),
      });
      setEditingExamId(null);
      setEditFormData({});
      alert("Exam updated successfully");
      await refetchExams();
    } catch (error) {
      alert("Error updating exam");
    }
  };

  const handleCancelEdit = () => {
    setEditingExamId(null);
    setEditFormData({});
  };

  const handlePlayExam = async (exam: CBTExamItem) => {
    try {
      await apiClient.updateCbtExam(exam.id, { status: "active" });
      alert(`Exam "${exam.title}" is now active`);
      await refetchExams();
    } catch (error) {
      alert("Error activating exam");
    }
  };

  const handleDeleteExam = async (examId: number, title: string) => {
    if (!confirm(`Are you sure you want to delete exam "${title}"?`)) return;
    try {
      await apiClient.deleteCbtExam(examId);
      alert("Exam deleted successfully");
      await refetchExams();
    } catch (error) {
      alert("Error deleting exam");
    }
  };

  return (
    <AppShell
      eyebrow="School Admin Dashboard"
      allowedRoles={["super_admin", "school_admin"]}
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
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <SectionTitle title="CBT Exams" description="Manage computer-based tests for students" />
              <Button onClick={() => setShowCreateForm(true)} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
                <Plus className="mr-2 h-4 w-4" />
                Create Exam
              </Button>
            </div>

            {showCreateForm && (
              <div className="mb-5 rounded-[24px] border border-white/10 bg-white/5 p-5">
                <div className="mb-4 flex items-center justify-between">
                  <p className="text-lg font-semibold text-white">Create New Exam</p>
                  <Button size="sm" variant="outline" onClick={() => setShowCreateForm(false)} className="border-white/20 text-[#9eb1cf]">
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Title *</label>
                    <input
                      type="text"
                      value={createForm.title}
                      onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                      className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                      placeholder="Mid-term Math"
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Class *</label>
                    <input
                      type="text"
                      value={createForm.student_class}
                      onChange={(e) => setCreateForm({ ...createForm, student_class: e.target.value })}
                      className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                      placeholder="SS1"
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Duration (min)</label>
                    <input
                      type="number"
                      value={createForm.duration_minutes}
                      onChange={(e) => setCreateForm({ ...createForm, duration_minutes: Number(e.target.value) })}
                      className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Status</label>
                    <select
                      value={createForm.status}
                      onChange={(e) => setCreateForm({ ...createForm, status: e.target.value })}
                      className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                      <option value="draft">Draft</option>
                    </select>
                  </div>
                </div>
                <div className="mt-4 flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowCreateForm(false)} className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                    Cancel
                  </Button>
                  <Button onClick={handleCreateExam} disabled={isSubmitting} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
                    {isSubmitting ? "Creating..." : "Create Exam"}
                  </Button>
                </div>
              </div>
            )}

            <div className="space-y-3">
              {examsLoading ? (
                <p className="text-center text-[#9eb1cf]">Loading exams…</p>
              ) : exams.length === 0 ? (
                <p className="text-center text-[#9eb1cf]">No CBT exams created yet</p>
              ) : (
                exams.map((exam) => (
                  <div key={exam.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex-1 min-w-[240px]">
                      {editingExamId === exam.id ? (
                        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
                          <div>
                            <label className="text-xs text-[#8ea4c8]">Title</label>
                            <input
                              type="text"
                              defaultValue={String(editFormData.title ?? exam.title)}
                              onChange={(e) => setEditFormData({ ...editFormData, title: e.target.value })}
                              className="mt-1 w-full rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
                            />
                          </div>
                          <div>
                            <label className="text-xs text-[#8ea4c8]">Class</label>
                            <input
                              type="text"
                              defaultValue={String(editFormData.student_class ?? exam.student_class)}
                              onChange={(e) => setEditFormData({ ...editFormData, student_class: e.target.value })}
                              className="mt-1 w-full rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
                            />
                          </div>
                          <div>
                            <label className="text-xs text-[#8ea4c8]">Duration</label>
                            <input
                              type="number"
                              defaultValue={Number(editFormData.duration_minutes ?? exam.duration_minutes)}
                              onChange={(e) => setEditFormData({ ...editFormData, duration_minutes: Number(e.target.value) })}
                              className="mt-1 w-full rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
                            />
                          </div>
                          <div>
                            <label className="text-xs text-[#8ea4c8]">Status</label>
                            <select
                              defaultValue={String(editFormData.status ?? exam.status)}
                              onChange={(e) => setEditFormData({ ...editFormData, status: e.target.value })}
                              className="mt-1 w-full rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
                            >
                              <option value="active">Active</option>
                              <option value="inactive">Inactive</option>
                              <option value="draft">Draft</option>
                            </select>
                          </div>
                        </div>
                      ) : (
                        <>
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
                        </>
                      )}
                    </div>
                    <div className="flex gap-2">
                      {editingExamId === exam.id ? (
                        <>
                          <Button size="sm" onClick={() => handleSaveEdit(exam.id)} className="bg-green-600 text-white hover:bg-green-700">
                            <Save className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={handleCancelEdit} className="border-white/20 text-[#9eb1cf]">
                            <X className="h-3 w-3" />
                          </Button>
                        </>
                      ) : (
                        <>
                          <Button size="sm" variant="outline" onClick={() => handleEditExam(exam)} className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handlePlayExam(exam)} className="border-green-500/30 text-green-500 hover:bg-green-500/10">
                            <Play className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleDeleteExam(exam.id, exam.title)} className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                            <Trash2 className="h-3 w-3" />
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

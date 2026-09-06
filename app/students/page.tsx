"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Upload, Plus, Edit, Trash2, Save, X } from "lucide-react";
import { getUser } from "@/services/auth-storage";
import { apiClient } from "@/services/api-client";
import { useStudentsQuery } from "@/hooks/use-crm-query";
import type { StudentItem } from "@/types/crm";

export default function StudentsPage() {
  const { data, isLoading, refetch } = useStudentsQuery();
  const [isImporting, setIsImporting] = useState(false);
  const [editingStudent, setEditingStudent] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState<{ first_name?: string; last_name?: string; admission_no?: string; gender?: string; date_of_birth?: string; class_id?: string; status?: string }>({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [addFormData, setAddFormData] = useState<Record<string, string>>({
    first_name: "",
    last_name: "",
    gender: "",
    date_of_birth: "",
    class_id: "",
    family_id: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "admissions_officer", "teacher"].includes(userRole);
  const canDelete = userRole === "school_admin";

  const studentRows: Array<StudentItem & { first_name: string; last_name: string; class_id?: string; family_id?: string }> =
    data?.students?.map((s) => ({
      ...s,
      first_name: s.fullName?.split(" ")[0] ?? "",
      last_name: s.fullName?.split(" ").slice(1).join(" ") ?? "",
      class_id: s.className,
      family_id: s.guardian,
    })) ?? [];

  const handleCSVImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsImporting(true);

    try {
      const result = await apiClient.importStudentsCSV(file);
      alert(`Successfully imported ${(result as { students_created?: number }).students_created ?? 0} students`);
      await refetch();
    } catch (error) {
      console.error('Error importing students:', error);
      alert('Error importing students');
    } finally {
      setIsImporting(false);
    }
  };

  const handleEdit = (student: { id: string; first_name: string; last_name: string; admission_no?: string; gender?: string; date_of_birth?: string; class_id?: string; status?: string; family_id?: string }) => {
    setEditingStudent(student.id);
    setEditFormData({
      first_name: student.first_name,
      last_name: student.last_name,
      admission_no: student.admission_no,
      gender: student.gender,
      date_of_birth: student.date_of_birth,
      class_id: student.class_id,
      status: student.status,
    });
  };

  const handleSaveEdit = async (studentId: string) => {
    try {
      await apiClient.updateStudent(studentId, editFormData);
      setEditingStudent(null);
      setEditFormData({});
      alert('Student updated successfully');
      await refetch();
    } catch (error) {
      alert('Error updating student');
    }
  };

  const handleCancelEdit = () => {
    setEditingStudent(null);
    setEditFormData({});
  };

  const handleDelete = async (studentId: string) => {
    if (!confirm('Are you sure you want to delete this student?')) return;

    try {
      await apiClient.deleteStudent(studentId);
      alert('Student deleted successfully');
      await refetch();
    } catch (error) {
      alert('Error deleting student');
    }
  };

  const handleAddStudent = async () => {
    if (!addFormData.first_name || !addFormData.last_name) {
      alert('First name and last name are required');
      return;
    }
    setIsSubmitting(true);
    try {
      await apiClient.createStudent({
        first_name: addFormData.first_name,
        last_name: addFormData.last_name,
        gender: addFormData.gender || undefined,
        date_of_birth: addFormData.date_of_birth || undefined,
        class_id: addFormData.class_id || undefined,
        family_id: addFormData.family_id || undefined,
      });
      alert('Student created successfully');
      setShowAddForm(false);
      setAddFormData({
        first_name: "",
        last_name: "",
        gender: "",
        date_of_birth: "",
        class_id: "",
        family_id: "",
      });
      await refetch();
    } catch (error) {
      alert('Error creating student');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelAdd = () => {
    setShowAddForm(false);
    setAddFormData({
      first_name: "",
      last_name: "",
      gender: "",
      date_of_birth: "",
      class_id: "",
      family_id: "",
    });
  };

  return (
    <AppShell
      eyebrow="Student Records"
      title="Student history, health, and performance"
      description="Bring attendance, behaviour, classroom placement, and medical context together so teachers and school operations always work from the same source of truth."
    >
      <div className="mb-6 flex flex-wrap gap-4">
        <Button
          onClick={() => setShowAddForm(true)}
          className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Student
        </Button>
        <div className="relative">
          <input
            type="file"
            accept=".csv"
            onChange={handleCSVImport}
            disabled={isImporting}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <Button
            variant="outline"
            disabled={isImporting}
            className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"
          >
            <Upload className="h-4 w-4 mr-2" />
            {isImporting ? 'Importing...' : 'Import CSV'}
          </Button>
        </div>
      </div>

      {showAddForm && (
        <div className="mb-6 rounded-[24px] border border-white/10 bg-white/5 p-5">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-lg font-semibold text-white">Add New Student</p>
            <Button size="sm" variant="outline" onClick={handleCancelAdd} className="border-white/20 text-[#9eb1cf]">
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">First Name *</label>
              <input
                type="text"
                value={addFormData.first_name}
                onChange={(e) => setAddFormData({ ...addFormData, first_name: e.target.value })}
                className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                placeholder="John"
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Last Name *</label>
              <input
                type="text"
                value={addFormData.last_name}
                onChange={(e) => setAddFormData({ ...addFormData, last_name: e.target.value })}
                className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                placeholder="Doe"
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Gender</label>
              <input
                type="text"
                value={addFormData.gender}
                onChange={(e) => setAddFormData({ ...addFormData, gender: e.target.value })}
                className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                placeholder="Male / Female"
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Date of Birth</label>
              <input
                type="date"
                value={addFormData.date_of_birth}
                onChange={(e) => setAddFormData({ ...addFormData, date_of_birth: e.target.value })}
                className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Class</label>
              <input
                type="text"
                value={addFormData.class_id}
                onChange={(e) => setAddFormData({ ...addFormData, class_id: e.target.value })}
                className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                placeholder="SS1"
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Family ID</label>
              <input
                type="text"
                value={addFormData.family_id}
                onChange={(e) => setAddFormData({ ...addFormData, family_id: e.target.value })}
                className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                placeholder="fam_xxx"
              />
            </div>
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={handleCancelAdd}
              className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"
            >
              Cancel
            </Button>
            <Button
              onClick={handleAddStudent}
              disabled={isSubmitting}
              className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
            >
              {isSubmitting ? 'Creating...' : 'Save Student'}
            </Button>
          </div>
        </div>
      )}

      {isLoading ? (
        <LoadingPanel />
      ) : (
        <DataTable
          title="Student directory"
          description="An operations-ready directory for administration, finance, and classroom support."
          columns={["Student", "Class", "Guardian", "Attendance", "Behaviour", "Medical", "Actions"]}
          rows={studentRows.map((student) => [
            editingStudent === student.id ? (
              <input
                key="first_name"
                type="text"
                value={editFormData.first_name ?? ""}
                onChange={(e) => setEditFormData({ ...editFormData, first_name: e.target.value })}
                className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
              />
            ) : (
              <Link key={student.id} href={`/students/${student.id}`} className="font-medium text-[#d9a441] hover:underline">
                {student.first_name} {student.last_name}
              </Link>
            ),
            editingStudent === student.id ? (
              <input
                key="class_id"
                type="text"
                value={editFormData.class_id ?? ""}
                onChange={(e) => setEditFormData({ ...editFormData, class_id: e.target.value })}
                className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
              />
            ) : (
              student.class_id || student.className || 'N/A'
            ),
            student.family_id || student.guardian || 'N/A',
            student.attendance || 'N/A',
            <Badge key={`${student.id}-behaviour`} tone="neutral">
              {student.behaviour || 'Active'}
            </Badge>,
            student.medicalFlag || 'N/A',
            <div key={`${student.id}-actions`} className="flex gap-2">
              {editingStudent === student.id ? (
                <>
                  <Button
                    size="sm"
                    onClick={() => handleSaveEdit(student.id)}
                    className="bg-green-600 text-white hover:bg-green-700"
                  >
                    <Save className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleCancelEdit}
                    variant="outline"
                    className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </>
              ) : (
                <>
                  {canEdit && (
                    <Button
                      size="sm"
                      onClick={() => handleEdit(student)}
                      variant="outline"
                      className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  )}
                  {canDelete && (
                    <Button
                      size="sm"
                      onClick={() => handleDelete(student.id)}
                      variant="outline"
                      className="border-red-500/30 text-red-500 hover:bg-red-500/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </>
              )}
            </div>,
          ])}
        />
      )}
    </AppShell>
  );
}

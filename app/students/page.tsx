"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Upload, Plus, Edit, Trash2, Save, X } from "lucide-react";
import { getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingStudent, setEditingStudent] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState({});

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "admission_officer", "teacher"].includes(userRole);
  const canDelete = userRole === "school_admin";

  const handleCSVImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/students/import/csv`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Successfully imported ${result.students_created} students`);
        // Refresh students list
      } else {
        const error = await response.json();
        alert(`Failed to import students: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error importing students:', error);
      alert('Error importing students');
    } finally {
      setIsImporting(false);
    }
  };

  const handleEdit = (student: any) => {
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
      const response = await fetch(`${API_URL}/students/${studentId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(editFormData),
      });

      if (response.ok) {
        setEditingStudent(null);
        alert('Student updated successfully');
        // Refresh students list
      } else {
        alert('Failed to update student');
      }
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
      const response = await fetch(`${API_URL}/students/${studentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        alert('Student deleted successfully');
        // Refresh students list
      } else {
        alert('Failed to delete student');
      }
    } catch (error) {
      alert('Error deleting student');
    }
  };

  return (
    <AppShell
      eyebrow="Student Records"
      title="Student history, health, and performance"
      description="Bring attendance, behaviour, classroom placement, and medical context together so teachers and school operations always work from the same source of truth."
    >
      <div className="mb-6 flex gap-4">
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

      {isLoading ? (
        <LoadingPanel />
      ) : (
        <DataTable
          title="Student directory"
          description="An operations-ready directory for administration, finance, and classroom support."
          columns={["Student", "Class", "Guardian", "Attendance", "Behaviour", "Medical", "Actions"]}
          rows={students.map((student: any) => [
            editingStudent === student.id ? (
              <input
                key="first_name"
                type="text"
                defaultValue={student.first_name}
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
                defaultValue={student.class_id || ''}
                onChange={(e) => setEditFormData({ ...editFormData, class_id: e.target.value })}
                className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
              />
            ) : (
              student.class_id || 'N/A'
            ),
            student.family_id || 'N/A',
            'N/A',
            <Badge key={`${student.id}-behaviour`} tone="neutral">
              Active
            </Badge>,
            'N/A',
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

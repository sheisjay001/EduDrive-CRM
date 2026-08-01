"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Upload, Plus } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

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
          columns={["Student", "Class", "Guardian", "Attendance", "Behaviour", "Medical"]}
          rows={students.map((student: any) => [
            <Link key={student.id} href={`/students/${student.id}`} className="font-medium text-[#d9a441] hover:underline">
              {student.first_name} {student.last_name}
            </Link>,
            student.class_id || 'N/A',
            student.family_id || 'N/A',
            'N/A',
            <Badge key={`${student.id}-behaviour`} tone="neutral">
              Active
            </Badge>,
            'N/A',
          ])}
        />
      )}
    </AppShell>
  );
}

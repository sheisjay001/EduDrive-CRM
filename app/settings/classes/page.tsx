"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Users, BookOpen, GraduationCap, Plus } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Class {
  id: string;
  class_name: string;
  class_code: string;
  class_level: string;
  name?: string;
  level?: string;
  section?: string;
  capacity: number;
  current_enrollment: number;
  student_count?: number;
  subject_count?: number;
  subjects?: Array<{ id: string; name: string; teacher_name: string }>;
}

interface Subject {
  id: string;
  subject_name: string;
  subject_code: string;
  teacher_name: string;
}

export default function ClassesPage() {
  const [classes, setClasses] = useState<Class[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateClassDialog, setShowCreateClassDialog] = useState(false);
  const [showCreateSubjectDialog, setShowCreateSubjectDialog] = useState(false);

  const fetchClasses = async () => {
    try {
      const response = await fetch(`${API_URL}/classes/`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setClasses(Array.isArray(data) ? data : data.classes || []);
      }
    } catch (error) {
      console.error("Error fetching classes:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useState(() => {
    fetchClasses();
  });

  const handleCreateClass = async (classData: Record<string, unknown>) => {
    try {
      const response = await fetch(`${API_URL}/classes/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(classData),
      });

      if (response.ok) {
        setShowCreateClassDialog(false);
        fetchClasses();
      }
    } catch (error) {
      console.error("Error creating class:", error);
    }
  };

  const handleCreateSubject = async (subjectData: Record<string, unknown>) => {
    try {
      const response = await fetch(`${API_URL}/classes/subjects`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(subjectData),
      });

      if (response.ok) {
        setShowCreateSubjectDialog(false);
        fetchClasses();
      }
    } catch (error) {
      console.error("Error creating subject:", error);
    }
  };

  const handlePromoteStudents = async (classId: string) => {
    try {
      const response = await fetch(`${API_URL}/classes/promote`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ class_id: classId }),
      });

      if (response.ok) {
        fetchClasses();
      }
    } catch (error) {
      console.error("Error promoting students:", error);
    }
  };

  return (
    <AppShell
      eyebrow="Class Structure"
      title="Academic organization and subject management"
      description="Configure classes, assign subjects and teachers, manage student enrollments, and handle promotions."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button variant="secondary">
                <GraduationCap className="mr-2 h-4 w-4" />
                Classes ({classes.length})
              </Button>
              <Button variant="secondary">
                <BookOpen className="mr-2 h-4 w-4" />
                Subjects ({classes.reduce((acc, classItem) => acc + (classItem.subjects?.length || 0), 0)})
              </Button>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => setShowCreateSubjectDialog(true)}>
                <BookOpen className="mr-2 h-4 w-4" />
                Add Subject
              </Button>
              <Button onClick={() => setShowCreateClassDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Class
              </Button>
            </div>
          </div>

          <div className="space-y-6">
            {classes.length === 0 ? (
              <Card className="p-6">
                <p className="text-center text-[#9eb1cf]">No classes configured</p>
              </Card>
            ) : (
              classes.map((classItem) => (
                <Card key={classItem.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-white">{classItem.name}</h3>
                        <Badge className="border-[#d9a441]/30 text-[#d9a441]">
                          {classItem.level}
                        </Badge>
                        <Badge className="border-white/20 text-white">
                          {classItem.section}
                        </Badge>
                      </div>
                      <div className="mt-3 flex items-center gap-4 text-sm text-[#9eb1cf]">
                        <span className="flex items-center gap-2">
                          <Users className="h-4 w-4" />
                          {classItem.student_count || 0} students
                        </span>
                        <span className="flex items-center gap-2">
                          <BookOpen className="h-4 w-4" />
                          {classItem.subject_count || 0} subjects
                        </span>
                        <span className="flex items-center gap-2">
                          Capacity: {classItem.capacity || "N/A"}
                        </span>
                      </div>
                      <div className="mt-4">
                        <p className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Assigned Subjects</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {classItem.subjects?.map((subject) => (
                            <Badge key={subject.id} className="border-white/20 text-white">
                              {subject.name} - {subject.teacher_name}
                            </Badge>
                          )) || <span className="text-sm text-[#9eb1cf]">No subjects assigned</span>}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => handlePromoteStudents(classItem.id)}
                        variant="outline"
                        className="border-green-500/30 text-green-500 hover:bg-green-500/10"
                      >
                        Promote
                      </Button>
                      <Button size="sm" variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                        Edit
                      </Button>
                      <Button size="sm" variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                        Delete
                      </Button>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </>
      )}
    </AppShell>
  );
}

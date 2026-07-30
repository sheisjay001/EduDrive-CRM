"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useStudentsQuery } from "@/hooks/use-crm-query";

export default function StudentsPage() {
  const { data, isLoading } = useStudentsQuery();

  return (
    <AppShell
      eyebrow="Student Records"
      title="Student history, health, and performance"
      description="Bring attendance, behaviour, classroom placement, and medical context together so teachers and school operations always work from the same source of truth."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <DataTable
          title="Student directory"
          description="An operations-ready directory for administration, finance, and classroom support."
          columns={["Student", "Class", "Guardian", "Attendance", "Behaviour", "Medical"]}
          rows={data.students.map((student) => [
            <Link key={student.id} href={`/students/${student.id}`} className="font-medium text-[#d9a441] hover:underline">
              {student.fullName}
            </Link>,
            student.className,
            student.guardian,
            student.attendance,
            <Badge key={`${student.id}-behaviour`} tone={student.behaviour === "Excellent" ? "good" : student.behaviour === "Good" ? "neutral" : "warn"}>
              {student.behaviour}
            </Badge>,
            student.medicalFlag,
          ])}
        />
      )}
    </AppShell>
  );
}

"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useParentsQuery } from "@/hooks/use-crm-query";

export default function ParentsPage() {
  const { data, isLoading } = useParentsQuery();

  return (
    <AppShell
      eyebrow="Parent Directory"
      title="Parent relationships"
      description="Manage guardian contacts, linked students, and channel preferences for parent communication."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <DataTable
          title="Parent index"
          description="A unified list of active parent contacts linked to student records."
          columns={["Parent", "Relationship", "Student", "Phone", "Email", "Status"]}
          rows={data.parents.map((parent) => [
            <Link key={parent.id} href={`/parents/${parent.id}`} className="font-medium text-[#d9a441] hover:underline">
              {parent.name}
            </Link>,
            parent.relationship,
            parent.studentName,
            parent.phone,
            parent.email,
            <Badge key={`${parent.id}-status`} tone={parent.status === "Active" ? "good" : "warn"}>
              {parent.status}
            </Badge>,
          ])}
        />
      )}
    </AppShell>
  );
}

"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useFamiliesQuery } from "@/hooks/use-crm-query";

export default function FamiliesPage() {
  const { data, isLoading } = useFamiliesQuery();

  return (
    <AppShell
      eyebrow="Household Management"
      title="See the full family picture"
      description="Organize siblings, primary contacts, balance ownership, and parent-facing communication around households instead of isolated student records."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <DataTable
          title="Active households"
          description="A single view of who is responsible for communication, billing, and student support."
          columns={["Household", "Guardians", "Students", "Balance", "Status"]}
          rows={data.households.map((family) => [
            <Link key={family.id} href={`/families/${family.id}`} className="font-medium text-[#d9a441] hover:underline">
              {family.householdName}
            </Link>,
            family.guardians.join(", "),
            `${family.students}`,
            family.balance,
            <Badge key={`${family.id}-status`} tone={family.status === "Up to date" ? "good" : "warn"}>
              {family.status}
            </Badge>,
          ])}
        />
      )}
    </AppShell>
  );
}

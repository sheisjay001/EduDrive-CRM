"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useStaffQuery } from "@/hooks/use-crm-query";

export default function StaffPage() {
  const { data, isLoading } = useStaffQuery();

  return (
    <AppShell
      eyebrow="Staff Operations"
      title="Attendance, responsiveness, and accountability"
      description="Give school leaders a simple view of who is showing up, who is responding quickly, and where operational performance is strongest."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="grid gap-4 xl:grid-cols-3">
            {data.metrics.map((metric) => (
              <Card key={metric.label}>
                <p className="text-sm font-semibold text-white">{metric.label}</p>
                <p className="mt-4 font-serif text-4xl text-[#f9d28a]">{metric.value}</p>
                <p className="mt-3 text-sm text-[#9eb1cf]">{metric.note}</p>
              </Card>
            ))}
          </div>
          <DataTable
            title="Staff watchlist"
            description="Daily visibility into service posture and operational consistency."
            columns={["Name", "Role", "Attendance", "Response time", "Performance signal"]}
            rows={data.people.map((person) => [
              person.name,
              person.role,
              person.attendance,
              person.responseTime,
              person.performance,
            ])}
          />
        </>
      )}
    </AppShell>
  );
}

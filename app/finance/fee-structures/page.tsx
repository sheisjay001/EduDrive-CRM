"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useFeeStructuresQuery } from "@/hooks/use-crm-query";

export default function FeeStructuresPage() {
  const { data, isLoading } = useFeeStructuresQuery();

  return (
    <AppShell
      eyebrow="Fee structure manager"
      title="Term fees and billing rules"
      description="Define class-level fee bundles, due date rules, and optional charges for the current term."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          {data.items.map((item) => (
            <Card key={item.id} className="space-y-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm text-[#9eb1cf]">{item.termName}</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{item.title}</p>
                </div>
                <Badge tone="neutral">{item.dueDays} days</Badge>
              </div>
              <p className="text-sm leading-7 text-[#d6dfef]">Class: {item.className}</p>
              <p className="text-3xl font-serif text-[#f9d28a]">{item.amount}</p>
              <div className="text-sm text-[#9eb1cf]">
                Fee bundles are used for invoice generation and debtor follow-up.
              </div>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}

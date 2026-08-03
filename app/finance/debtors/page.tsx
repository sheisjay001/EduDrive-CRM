"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useFinanceQuery } from "@/hooks/use-crm-query";
import type { KpiCard } from "@/types/crm";

export default function FinanceDebtorsPage() {
  const { data, isLoading } = useFinanceQuery();

  if (isLoading || !data) {
    return (
      <AppShell
        eyebrow="Debtors Dashboard"
        title="Outstanding balances that need action"
        description="Prioritize collection follow-up by age, balance size, and the last family touchpoint."
      >
        <LoadingPanel />
      </AppShell>
    );
  }

  const longAgingCount = data.debtors.filter((debtor) => debtor.aging.includes("31")).length;

  const kpis: KpiCard[] = [
    { label: "Overdue balance", value: data.summary.overdue, change: "Current debtor exposure", tone: "danger" },
    { label: "Watchlist families", value: String(data.debtors.length), change: "Active collection cases", tone: "warn" },
    { label: "31+ day cases", value: String(longAgingCount), change: "Needs senior follow-up", tone: "danger" },
    { label: "Collection rate", value: data.summary.collectionRate, change: "Recovery pace this term", tone: "good" },
  ];

  return (
    <AppShell
      eyebrow="Debtors Dashboard"
      title="Outstanding balances that need action"
      description="Prioritize collection follow-up by age, balance size, and the last family touchpoint."
    >
      <div className="flex flex-wrap gap-3">
        <Button asChild variant="secondary">
          <Link href="/finance">Back to finance overview</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/finance/payments">Open payment desk</Link>
        </Button>
      </div>

      <KpiGrid items={kpis} />

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <DataTable
          title="Debtor queue"
          description="Families and students needing the next collection action, grouped around aging and recent contact context."
          columns={["Student", "Class", "Balance", "Aging", "Last contact", "Next move"]}
          rows={data.debtors.map((debtor) => [
            debtor.student,
            debtor.className,
            debtor.balance,
            <Badge key={`${debtor.student}-aging`} tone={debtor.aging.includes("31") ? "danger" : debtor.aging.includes("16") ? "warn" : "neutral"}>
              {debtor.aging}
            </Badge>,
            debtor.lastContact,
            debtor.aging.includes("31") ? "Escalate to payment plan review" : "Send reminder and confirm date",
          ])}
        />

        <div className="space-y-6">
          <Card className="space-y-5">
            <SectionTitle
              title="Collection ladder"
              description="A simple rhythm for moving from reminder to resolution without losing parent trust."
            />
            <div className="space-y-3">
              {[
                "0-15 days: reminder message with receipt-ready payment instructions.",
                "16-30 days: direct bursary call and confirmed promise-to-pay date.",
                "31+ days: payment plan conversation and school leadership visibility.",
              ].map((step) => (
                <div key={step} className="rounded-[24px] border border-white/10 bg-white/5 p-4 text-sm text-[#d6dfef]">
                  {step}
                </div>
              ))}
            </div>
          </Card>

          <Card className="space-y-4">
            <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Desk note</p>
            <p className="text-sm leading-7 text-[#c1cee3]">
              The debtor view works best when every balance has a visible owner, the last outreach is logged, and the next commitment is dated before the record leaves today&apos;s queue.
            </p>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

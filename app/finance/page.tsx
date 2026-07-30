"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { DataTable, KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useFeeStructuresQuery, useFinanceQuery } from "@/hooks/use-crm-query";

export default function FinancePage() {
  const { data, isLoading } = useFinanceQuery();
  const { data: feeData, isLoading: feeLoading } = useFeeStructuresQuery();

  const kpis = [
    { label: "Total billed", value: data?.summary.totalBilled ?? "", change: "Term-wide billing volume", tone: "neutral" as const },
    { label: "Collected", value: data?.summary.totalCollected ?? "", change: "Includes online and offline", tone: "good" as const },
    { label: "Overdue", value: data?.summary.overdue ?? "", change: "Needs follow-up attention", tone: "warn" as const },
    { label: "Collection rate", value: data?.summary.collectionRate ?? "", change: "Recovery for current term", tone: "good" as const },
  ];

  return (
    <AppShell
      eyebrow="Finance Operations"
      title="Collections, invoices, and debt visibility"
      description="Give the bursary team one place to track term billing, payment status, debt aging, and the next best collection action."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <KpiGrid items={kpis} />
          <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
            <DataTable
              title="Invoice desk"
              description="Recent invoices with payment posture and due-date context."
              columns={["Invoice", "Student", "Term", "Amount due", "Amount paid", "Due date", "Status"]}
              rows={data.invoices.map((invoice) => [
                <Link key={`${invoice.id}-link`} href={`/finance/invoices/${invoice.id}`} className="font-medium text-[#d9a441] hover:underline">
                  {invoice.id}
                </Link>,
                invoice.student,
                invoice.term,
                invoice.amountDue,
                invoice.amountPaid,
                invoice.dueDate,
                <Badge key={`${invoice.id}-status`} tone={invoice.status === "Paid" ? "good" : invoice.status === "Overdue" ? "danger" : "warn"}>
                  {invoice.status}
                </Badge>,
              ])}
            />
            <div className="space-y-6">
              <Card className="space-y-5">
                <SectionTitle title="Fee structure manager" description="Term-driven class fees, due dates, and optional charges for the bursary team." />
                {feeLoading || !feeData ? (
                  <LoadingPanel />
                ) : (
                  <div className="space-y-3">
                    {feeData.items.slice(0, 3).map((item) => (
                      <div key={item.id} className="rounded-[28px] border border-white/10 bg-white/5 p-5">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <p className="text-sm font-semibold text-white">{item.title}</p>
                            <p className="mt-1 text-sm text-[#9eb1cf]">{item.className} • {item.termName}</p>
                          </div>
                          <Badge tone="neutral">Due {item.dueDays} days</Badge>
                        </div>
                        <p className="mt-4 text-3xl font-serif text-[#f9d28a]">{item.amount}</p>
                      </div>
                    ))}
                    <div className="text-sm text-[#9eb1cf]">
                      <Link href="/finance/fee-structures" className="text-[#d9a441] underline">
                        View full fee structure manager
                      </Link>
                    </div>
                  </div>
                )}
              </Card>
              <Card className="space-y-5">
                <SectionTitle title="Debtor watchlist" description="Families who need immediate collections outreach or payment plan follow-up." />
                <div className="space-y-3">
                  {data.debtors.map((debtor) => (
                    <div key={debtor.student} className="rounded-[28px] border border-white/10 bg-white/5 p-5">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold text-white">{debtor.student}</p>
                          <p className="mt-1 text-sm text-[#9eb1cf]">{debtor.className}</p>
                        </div>
                        <Badge tone="danger">{debtor.aging}</Badge>
                      </div>
                      <p className="mt-4 font-serif text-3xl text-[#f9d28a]">{debtor.balance}</p>
                      <p className="mt-2 text-sm text-[#9eb1cf]">{debtor.lastContact}</p>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}

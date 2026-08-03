"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, KpiGrid, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { useFinanceQuery } from "@/hooks/use-crm-query";
import type { KpiCard } from "@/types/crm";

type PaymentDeskItem = {
  receiptRef: string;
  invoiceId: string;
  student: string;
  method: string;
  amount: string;
  postedAt: string;
  status: "Settled" | "Part paid";
};

function buildPaymentDesk(invoices: Array<{ id: string; student: string; amountPaid: string; dueDate: string; status: string }>): PaymentDeskItem[] {
  return invoices
    .filter((invoice) => invoice.amountPaid !== "NGN 0")
    .map((invoice, index) => ({
      receiptRef: `RCT-${invoice.id.replace("INV-", "")}`,
      invoiceId: invoice.id,
      student: invoice.student,
      method: invoice.status === "Part paid" ? "Paystack" : index % 2 === 0 ? "Bank transfer" : "Cash office",
      amount: invoice.amountPaid,
      postedAt: invoice.status === "Paid" ? invoice.dueDate : "Posted during current term",
      status: invoice.status === "Part paid" ? "Part paid" : "Settled",
    }));
}

export default function FinancePaymentsPage() {
  const { data, isLoading } = useFinanceQuery();

  if (isLoading || !data) {
    return (
      <AppShell
        eyebrow="Payments Desk"
        title="Payment records and receipt flow"
        description="Track every posted payment, verify how it was received, and follow through on receipt delivery."
      >
        <LoadingPanel />
      </AppShell>
    );
  }

  const payments = buildPaymentDesk(data.invoices);
  const settledCount = payments.filter((payment) => payment.status === "Settled").length;
  const partPaidCount = payments.length - settledCount;

  const kpis: KpiCard[] = [
    { label: "Collected", value: data.summary.totalCollected, change: "Current term posted payments", tone: "good" },
    { label: "Receipt records", value: String(payments.length), change: "Rows in the payment desk", tone: "neutral" },
    { label: "Settled invoices", value: String(settledCount), change: "Fully cleared billing items", tone: "good" },
    { label: "Part paid", value: String(partPaidCount), change: "Needs collection follow-up", tone: "warn" },
  ];

  return (
    <AppShell
      eyebrow="Payments Desk"
      title="Payment records and receipt flow"
      description="Track every posted payment, verify how it was received, and follow through on receipt delivery."
    >
      <div className="flex flex-wrap gap-3">
        <Button asChild variant="secondary">
          <Link href="/finance">Back to finance overview</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/finance/debtors">Open debtors dashboard</Link>
        </Button>
      </div>

      <KpiGrid items={kpis} />

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <DataTable
          title="Posted payments"
          description="Ledger-style view of the payments already attached to invoices in the current operating window."
          columns={["Receipt", "Student", "Invoice", "Method", "Amount", "Posted", "Status"]}
          rows={payments.map((payment) => [
            payment.receiptRef,
            payment.student,
            <Link key={`${payment.invoiceId}-link`} href={`/finance/invoices/${payment.invoiceId}`} className="font-medium text-[#d9a441] hover:underline">
              {payment.invoiceId}
            </Link>,
            payment.method,
            payment.amount,
            payment.postedAt,
            <Badge key={`${payment.receiptRef}-status`} tone={payment.status === "Settled" ? "good" : "warn"}>
              {payment.status}
            </Badge>,
          ])}
        />

        <div className="space-y-6">
          <Card className="space-y-5">
            <SectionTitle
              title="Receipt workflow"
              description="Operational checks that keep payment evidence, collections, and parent communication aligned."
            />
            <div className="space-y-3">
              {[
                "Match every posted amount to a student invoice before close of day.",
                "Send receipt confirmation as soon as a payment clears or is manually approved.",
                "Escalate part-paid invoices into the debtors follow-up queue with the next agreed date.",
              ].map((item) => (
                <div key={item} className="rounded-[24px] border border-white/10 bg-white/5 p-4 text-sm text-[#d6dfef]">
                  {item}
                </div>
              ))}
            </div>
          </Card>

          <Card className="space-y-4">
            <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Channel posture</p>
            <div className="space-y-3">
              <div className="rounded-[24px] border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-semibold text-white">Online collections</p>
                <p className="mt-2 text-sm text-[#9eb1cf]">Paystack and gateway-linked payments should move straight into receipt dispatch once verified.</p>
              </div>
              <div className="rounded-[24px] border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-semibold text-white">Offline collections</p>
                <p className="mt-2 text-sm text-[#9eb1cf]">Cash and transfer records still need the same invoice match and acknowledgement discipline.</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

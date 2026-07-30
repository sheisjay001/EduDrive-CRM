"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useInvoiceQuery } from "@/hooks/use-crm-query";

export default function InvoiceDetailPage() {
  const params = useParams();
  const invoiceId = Array.isArray(params?.invoiceId) ? params.invoiceId[0] : params?.invoiceId ?? "";
  const { data, isLoading } = useInvoiceQuery(invoiceId);

  return (
    <AppShell
      eyebrow="Invoice detail"
      title="Invoice record"
      description="See payment status, line items, and collection notes for a single student invoice."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <Card className="space-y-6">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Invoice</p>
              <p className="mt-3 text-3xl font-semibold text-white">{data.id}</p>
              <div className="mt-3 flex flex-wrap gap-3">
                <Badge tone={data.status === "Paid" ? "good" : data.status === "Overdue" ? "danger" : "warn"}>{data.status}</Badge>
                <Badge tone="neutral">{data.term}</Badge>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[#9eb1cf]">Student</p>
                <p className="mt-2 text-lg text-white">{data.student}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Issue date</p>
                <p className="mt-2 text-lg text-white">{data.issuedAt}</p>
              </div>
            </div>

            <div>
              <p className="text-sm text-[#9eb1cf]">Billing items</p>
              <div className="mt-4 space-y-3">
                {data.lineItems.map((item) => (
                  <div key={item.code} className="rounded-[24px] border border-white/10 bg-white/5 p-4 text-sm text-[#d6dfef]">
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-semibold text-white">{item.description}</p>
                      <p>{item.amount}</p>
                    </div>
                    <p className="mt-2 text-xs text-[#9eb1cf]">Code: {item.code}</p>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card className="space-y-5">
            <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Payment history</p>
            {data.payments.length === 0 ? (
              <p className="text-sm leading-7 text-[#9eb1cf]">No payments have been received for this invoice.</p>
            ) : (
              <div className="space-y-3">
                {data.payments.map((payment) => (
                  <div key={payment.paidAt} className="rounded-[24px] border border-white/10 bg-white/5 p-4 text-sm text-[#d6dfef]">
                    <p className="font-semibold text-white">{payment.method}</p>
                    <p className="mt-2 text-sm text-[#9eb1cf]">Amount: {payment.amount}</p>
                    <p className="mt-1 text-sm text-[#9eb1cf]">Paid at {payment.paidAt}</p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}
    </AppShell>
  );
}

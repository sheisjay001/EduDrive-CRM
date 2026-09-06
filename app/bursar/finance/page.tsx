"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, SectionTitle } from "@/components/dashboard/ops-primitives";
import { CreditCard, TrendingUp, AlertCircle, DollarSign, FileText, Download, Plus } from "lucide-react";

export default function BursarFinancePage() {
  return (
    <AppShell
      eyebrow="Bursar Portal"
      title="Finance Operations"
      description="Manage invoices, payments, fee structures, and debt collection."
      allowedRoles={["bursar"]}
    >
      <KpiGrid items={[
        { label: "Total Billed", value: "₦1.2M", change: "Term-wide billing", tone: "neutral" },
        { label: "Collected", value: "₦850K", change: "Includes online/offline", tone: "good" },
        { label: "Overdue", value: "₦350K", change: "Needs follow-up", tone: "warn" },
        { label: "Collection Rate", value: "71%", change: "Current term recovery", tone: "good" },
      ]} />

      <div className="grid gap-6 mt-6">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <SectionTitle title="Invoice Management" description="Create and manage student invoices" />
            <button className="flex items-center gap-2 rounded-lg border border-[#d9a441]/30 bg-[#d9a441]/10 px-3 py-1.5 text-sm text-white transition-all hover:bg-[#d9a441]/20">
              <Plus className="h-4 w-4" />
              Create Invoice
            </button>
          </div>
          <div className="space-y-3">
            {[
              { id: "INV-001", student: "John Doe", class: "JSS 2A", amount: "₦45,000", due: "Sep 15", status: "Paid" },
              { id: "INV-002", student: "Jane Smith", class: "SS 1B", amount: "₦45,000", due: "Sep 15", status: "Paid" },
              { id: "INV-003", student: "Michael Brown", class: "JSS 2A", amount: "₦45,000", due: "Sep 20", status: "Pending" },
              { id: "INV-004", student: "Sarah Johnson", class: "SS 1A", amount: "₦45,000", due: "Sep 10", status: "Overdue" },
            ].map((invoice, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                    <FileText className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{invoice.id}</p>
                    <p className="text-sm text-[#9eb1cf]">{invoice.student} • {invoice.class}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-white">{invoice.amount}</p>
                  <Badge tone={invoice.status === "Paid" ? "good" : invoice.status === "Overdue" ? "danger" : "warn"}>
                    {invoice.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Fee Structure" description="Current term fee configuration" />
          <div className="grid gap-3 md:grid-cols-2 mt-4">
            {[
              { class: "JSS 1-3", amount: "₦45,000/term", items: "Tuition + Materials" },
              { class: "SS 1-3", amount: "₦50,000/term", items: "Tuition + Materials + Lab" },
              { class: "Primary 1-6", amount: "₦35,000/term", items: "Tuition + Materials" },
              { class: "Nursery", amount: "₦30,000/term", items: "Tuition + Care" },
            ].map((fee, idx) => (
              <div key={idx} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-semibold text-white">{fee.class}</p>
                  <p className="text-lg font-semibold text-[#d9a441]">{fee.amount}</p>
                </div>
                <p className="text-sm text-[#9eb1cf]">{fee.items}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Reports & Exports" description="Generate financial reports" />
          <div className="grid gap-3 md:grid-cols-3 mt-4">
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Download className="h-4 w-4" />
              Collection Report
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Download className="h-4 w-4" />
              Debtors List
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Download className="h-4 w-4" />
              Payment History
            </button>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

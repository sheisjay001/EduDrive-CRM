"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, SectionTitle } from "@/components/dashboard/ops-primitives";
import { FileText, TrendingUp, Download, Calendar, DollarSign, BarChart3 } from "lucide-react";

export default function BursarReportsPage() {
  return (
    <AppShell
      eyebrow="Bursar Portal"
      title="Financial Reports"
      description="Generate and view financial reports and analytics."
      allowedRoles={["bursar"]}
    >
      <KpiGrid items={[
        { label: "Total Revenue", value: "₦1.2M", change: "+18% this term", tone: "good" },
        { label: "Collection Rate", value: "71%", change: "+5% vs last term", tone: "good" },
        { label: "Active Debtors", value: "23", change: "-3 from last month", tone: "warn" },
        { label: "Avg Payment Time", value: "12 days", change: "-2 days improvement", tone: "good" },
      ]} />

      <div className="grid gap-6 mt-6">
        <Card className="p-6">
          <SectionTitle title="Revenue Trends" description="Monthly revenue comparison" />
          <div className="space-y-4 mt-4">
            {[
              { month: "September", revenue: "₦450K", change: "+15%", trend: "up" },
              { month: "August", revenue: "₦390K", change: "+8%", trend: "up" },
              { month: "July", revenue: "₦360K", change: "-5%", trend: "down" },
              { month: "June", revenue: "₦380K", change: "+2%", trend: "up" },
            ].map((data, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                    <Calendar className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{data.month}</p>
                    <p className="text-sm text-[#9eb1cf]">Monthly Revenue</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-white">{data.revenue}</p>
                  <Badge tone={data.trend === "up" ? "good" : "warn"}>
                    {data.change}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Generate Reports" description="Download financial reports" />
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3 mt-4">
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Download className="h-4 w-4" />
              Collection Report
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Download className="h-4 w-4" />
              Debtors Report
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Download className="h-4 w-4" />
              Payment History
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <BarChart3 className="h-4 w-4" />
              Revenue Analysis
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <DollarSign className="h-4 w-4" />
              Fee Structure Report
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <FileText className="h-4 w-4" />
              Term Summary
            </button>
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Class-wise Collections" description="Revenue by class level" />
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4 mt-4">
            {[
              { class: "JSS 1-3", collected: "₦420K", target: "₦540K", rate: "78%" },
              { class: "SS 1-3", collected: "₦350K", target: "₦450K", rate: "78%" },
              { class: "Primary 1-6", collected: "₦280K", target: "₦420K", rate: "67%" },
              { class: "Nursery", collected: "₦120K", target: "₦180K", rate: "67%" },
            ].map((data, idx) => (
              <div key={idx} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="font-semibold text-white mb-2">{data.class}</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-[#9eb1cf]">Collected</span>
                    <span className="text-white">{data.collected}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-[#9eb1cf]">Target</span>
                    <span className="text-white">{data.target}</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                    <div className={`h-full rounded-full ${
                      parseInt(data.rate) >= 80 ? "bg-green-500" :
                      parseInt(data.rate) >= 70 ? "bg-[#d9a441]" :
                      "bg-red-500"
                    }`} style={{ width: data.rate }} />
                  </div>
                  <p className="text-xs text-[#9eb1cf] text-center">{data.rate} collected</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

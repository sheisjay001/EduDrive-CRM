"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { KpiGrid, SectionTitle } from "@/components/dashboard/ops-primitives";
import { Users, TrendingUp, Clock, CheckCircle, AlertCircle, Phone, Mail } from "lucide-react";

export default function AdmissionsOfficerDashboardPage() {
  return (
    <AppShell
      eyebrow="Admissions Portal"
      title="Admissions Dashboard"
      description="Track leads, conversions, and enrollment pipeline."
      allowedRoles={["admissions_officer"]}
    >
      <KpiGrid items={[
        { label: "Active Leads", value: "45", change: "+12 this week", tone: "neutral" },
        { label: "Conversions", value: "23", change: "+8% conversion rate", tone: "good" },
        { label: "Pending Follow-up", value: "18", change: "Needs attention", tone: "warn" },
        { label: "Enrolled This Term", value: "156", change: "+15% vs last term", tone: "good" },
      ]} />

      <div className="grid gap-6 mt-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="p-6">
          <SectionTitle title="Recent Leads" description="Latest inquiries and applications" />
          <div className="space-y-3 mt-4">
            {[
              { name: "John Doe", stage: "Inquiry", date: "Today", contact: "john@example.com" },
              { name: "Jane Smith", stage: "Application", date: "Yesterday", contact: "jane@example.com" },
              { name: "Michael Brown", stage: "Assessment", date: "2 days ago", contact: "michael@example.com" },
              { name: "Sarah Johnson", stage: "Offer", date: "3 days ago", contact: "sarah@example.com" },
            ].map((lead, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                    <Users className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{lead.name}</p>
                    <p className="text-sm text-[#9eb1cf]">{lead.contact}</p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge tone={lead.stage === "Offer" ? "good" : lead.stage === "Assessment" ? "warn" : "neutral"}>
                    {lead.stage}
                  </Badge>
                  <p className="text-sm text-[#9eb1cf] mt-1">{lead.date}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Quick Actions" description="Common admissions tasks" />
          <div className="grid gap-3 mt-4">
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Users className="h-4 w-4" />
              Add New Lead
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Phone className="h-4 w-4" />
              Schedule Call
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <Mail className="h-4 w-4" />
              Send Follow-up Email
            </button>
            <button className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white transition-all hover:bg-white/10">
              <CheckCircle className="h-4 w-4" />
              Convert Lead
            </button>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 mt-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <SectionTitle title="Pipeline Overview" description="Leads by stage" />
          <div className="space-y-3 mt-4">
            {[
              { stage: "Inquiry", count: 15, color: "bg-blue-500" },
              { stage: "Application", count: 12, color: "bg-yellow-500" },
              { stage: "Assessment", count: 8, color: "bg-orange-500" },
              { stage: "Offer", count: 6, color: "bg-green-500" },
              { stage: "Enrolled", count: 4, color: "bg-[#d9a441]" },
            ].map((pipeline, idx) => (
              <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-3">
                  <div className={`h-3 w-3 rounded-full ${pipeline.color}`} />
                  <p className="font-medium text-white">{pipeline.stage}</p>
                </div>
                <div className="flex items-center gap-4">
                  <p className="font-semibold text-white">{pipeline.count} leads</p>
                  <div className="h-2 w-24 rounded-full bg-white/10 overflow-hidden">
                    <div className={`h-full rounded-full ${pipeline.color}`} style={{ width: `${(pipeline.count / 15) * 100}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <SectionTitle title="Follow-up Reminders" description="Leads needing attention" />
          <div className="space-y-3 mt-4">
            {[
              { name: "Emma Davis", reason: "Application incomplete", days: "2 days ago" },
              { name: "James Miller", reason: "Assessment scheduled", days: "Today" },
              { name: "Olivia Garcia", reason: "Offer pending response", days: "Yesterday" },
            ].map((reminder, idx) => (
              <div key={idx} className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 p-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-500/20 text-red-400">
                  <AlertCircle className="h-4 w-4" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-white text-sm">{reminder.name}</p>
                  <p className="text-xs text-[#9eb1cf]">{reminder.reason}</p>
                </div>
                <p className="text-xs text-[#9eb1cf]">{reminder.days}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </AppShell>
  );
}

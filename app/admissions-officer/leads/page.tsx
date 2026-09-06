"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Phone, Mail, Calendar, Search, Filter } from "lucide-react";

export default function AdmissionsOfficerLeadsPage() {
  return (
    <AppShell
      eyebrow="Admissions Portal"
      title="Lead Management"
      description="Track and manage prospective student inquiries."
      allowedRoles={["admissions_officer"]}
    >
      <Card className="p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9eb1cf]" />
            <input
              type="text"
              placeholder="Search leads..."
              className="w-full rounded-lg border border-white/20 bg-white/10 pl-10 pr-4 py-2 text-sm text-white placeholder:text-[#9eb1cf] focus:border-[#d9a441] focus:outline-none"
            />
          </div>
          <button className="flex items-center gap-2 rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm text-white hover:bg-white/20">
            <Filter className="h-4 w-4" />
            Filter
          </button>
        </div>

        <div className="space-y-3">
          {[
            { name: "John Doe", email: "john@example.com", phone: "+234 801 234 5678", stage: "Inquiry", date: "Sep 6, 2026", source: "Website" },
            { name: "Jane Smith", email: "jane@example.com", phone: "+234 802 345 6789", stage: "Application", date: "Sep 5, 2026", source: "Referral" },
            { name: "Michael Brown", email: "michael@example.com", phone: "+234 803 456 7890", stage: "Assessment", date: "Sep 4, 2026", source: "School Fair" },
            { name: "Sarah Johnson", email: "sarah@example.com", phone: "+234 804 567 8901", stage: "Offer", date: "Sep 3, 2026", source: "Website" },
            { name: "Emma Davis", email: "emma@example.com", phone: "+234 805 678 9012", stage: "Inquiry", date: "Sep 2, 2026", source: "Social Media" },
          ].map((lead, idx) => (
            <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                  <Users className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-semibold text-white">{lead.name}</p>
                  <div className="flex items-center gap-3 mt-1">
                    <p className="text-sm text-[#9eb1cf] flex items-center gap-1">
                      <Mail className="h-3 w-3" />
                      {lead.email}
                    </p>
                    <p className="text-sm text-[#9eb1cf] flex items-center gap-1">
                      <Phone className="h-3 w-3" />
                      {lead.phone}
                    </p>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <Badge tone={lead.stage === "Offer" ? "good" : lead.stage === "Assessment" ? "warn" : "neutral"}>
                  {lead.stage}
                </Badge>
                <p className="text-sm text-[#9eb1cf] mt-1 flex items-center gap-1 justify-end">
                  <Calendar className="h-3 w-3" />
                  {lead.date}
                </p>
                <p className="text-xs text-[#9eb1cf] mt-1">{lead.source}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </AppShell>
  );
}

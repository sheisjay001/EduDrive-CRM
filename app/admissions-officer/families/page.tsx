"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Home, DollarSign, Search } from "lucide-react";

export default function AdmissionsOfficerFamiliesPage() {
  return (
    <AppShell
      eyebrow="Admissions Portal"
      title="Family Management"
      description="View and manage family information for enrolled and prospective students."
      allowedRoles={["admissions_officer"]}
    >
      <Card className="p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9eb1cf]" />
            <input
              type="text"
              placeholder="Search families..."
              className="w-full rounded-lg border border-white/20 bg-white/10 pl-10 pr-4 py-2 text-sm text-white placeholder:text-[#9eb1cf] focus:border-[#d9a441] focus:outline-none"
            />
          </div>
        </div>

        <div className="space-y-3">
          {[
            { name: "Doe Family", guardians: "John Doe, Mary Doe", students: 2, balance: "₦0", status: "Active" },
            { name: "Smith Family", guardians: "Robert Smith", students: 1, balance: "₦45,000", status: "Pending" },
            { name: "Brown Family", guardians: "Michael Brown, Linda Brown", students: 3, balance: "₦135,000", status: "Active" },
            { name: "Johnson Family", guardians: "David Johnson", students: 1, balance: "₦0", status: "Active" },
            { name: "Davis Family", guardians: "James Davis, Sarah Davis", students: 2, balance: "₦90,000", status: "Pending" },
          ].map((family, idx) => (
            <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                  <Home className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-semibold text-white">{family.name}</p>
                  <p className="text-sm text-[#9eb1cf]">{family.guardians}</p>
                  <p className="text-xs text-[#9eb1cf] flex items-center gap-1 mt-1">
                    <Users className="h-3 w-3" />
                    {family.students} student{family.students > 1 ? 's' : ''}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className={`font-semibold ${family.balance === "₦0" ? "text-green-400" : "text-yellow-400"}`}>
                  {family.balance}
                </p>
                <Badge tone={family.status === "Active" ? "good" : "warn"}>
                  {family.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </AppShell>
  );
}

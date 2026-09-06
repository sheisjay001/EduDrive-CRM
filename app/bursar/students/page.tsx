"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, DollarSign, AlertCircle, CheckCircle, Search } from "lucide-react";

export default function BursarStudentsPage() {
  return (
    <AppShell
      eyebrow="Bursar Portal"
      title="Student Fee Status"
      description="View payment status and fee balances for all students."
      allowedRoles={["bursar"]}
    >
      <Card className="p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9eb1cf]" />
            <input
              type="text"
              placeholder="Search students..."
              className="w-full rounded-lg border border-white/20 bg-white/10 pl-10 pr-4 py-2 text-sm text-white placeholder:text-[#9eb1cf] focus:border-[#d9a441] focus:outline-none"
            />
          </div>
          <select className="rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none">
            <option value="">All Classes</option>
            <option value="jss1">JSS 1</option>
            <option value="jss2">JSS 2</option>
            <option value="jss3">JSS 3</option>
            <option value="ss1">SS 1</option>
            <option value="ss2">SS 2</option>
            <option value="ss3">SS 3</option>
          </select>
          <select className="rounded-lg border border-white/20 bg-white/10 px-4 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none">
            <option value="">All Status</option>
            <option value="paid">Paid</option>
            <option value="pending">Pending</option>
            <option value="overdue">Overdue</option>
          </select>
        </div>

        <div className="space-y-3">
          {[
            { name: "John Doe", class: "JSS 2A", balance: "₦0", status: "Paid", term: "Current" },
            { name: "Jane Smith", class: "SS 1B", balance: "₦0", status: "Paid", term: "Current" },
            { name: "Michael Brown", class: "JSS 2A", balance: "₦45,000", status: "Pending", term: "Current" },
            { name: "Sarah Johnson", class: "SS 1A", balance: "₦90,000", status: "Overdue", term: "Current" },
            { name: "Emma Davis", class: "SS 1B", balance: "₦135,000", status: "Overdue", term: "Current" },
            { name: "James Miller", class: "JSS 2A", balance: "₦45,000", status: "Pending", term: "Current" },
            { name: "Olivia Garcia", class: "SS 1A", balance: "₦0", status: "Paid", term: "Current" },
            { name: "William Martinez", class: "JSS 2B", balance: "₦45,000", status: "Pending", term: "Current" },
          ].map((student, idx) => (
            <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center gap-3">
                <div className={`flex h-10 w-10 items-center justify-center rounded-full ${
                  student.status === "Paid" ? "bg-green-500/20 text-green-400" :
                  student.status === "Overdue" ? "bg-red-500/20 text-red-400" :
                  "bg-yellow-500/20 text-yellow-400"
                }`}>
                  {student.status === "Paid" ? <CheckCircle className="h-5 w-5" /> :
                   student.status === "Overdue" ? <AlertCircle className="h-5 w-5" /> :
                   <DollarSign className="h-5 w-5" />}
                </div>
                <div>
                  <p className="font-semibold text-white">{student.name}</p>
                  <p className="text-sm text-[#9eb1cf]">{student.class} • {student.term} Term</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`font-semibold ${
                  student.balance === "₦0" ? "text-green-400" :
                  student.status === "Overdue" ? "text-red-400" :
                  "text-yellow-400"
                }`}>
                  {student.balance}
                </p>
                <Badge tone={student.status === "Paid" ? "good" : student.status === "Overdue" ? "danger" : "warn"}>
                  {student.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </AppShell>
  );
}

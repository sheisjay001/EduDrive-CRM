"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Users, BookOpen, CalendarDays, FileText, TrendingUp, AlertCircle } from "lucide-react";
import { getAccessToken, getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Child {
  id: string;
  full_name: string;
  class?: string;
  grade?: string;
  date_of_birth?: string;
  student_id?: string;
  admission_number?: string;
  attendance?: string;
  behaviour?: string;
  medical_flag?: string;
  fee_status?: string;
}

export default function ParentStudentsPage() {
  const [loading, setLoading] = useState(true);
  const [children, setChildren] = useState<Child[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    fetch(`${API_URL}/parent/children`, { headers })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) setChildren(data.children || data || []);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell
      eyebrow="Parent Portal"
      title="My Children"
      description="View your children's academic records, attendance, behavior, and medical information."
      allowedRoles={["parent"]}
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <div className="space-y-6">
          {children.length === 0 ? (
            <Card className="p-12 text-center">
              <Users className="h-16 w-16 mx-auto text-[#9eb1cf] mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Children Linked</h3>
              <p className="text-[#9eb1cf]">No children are currently linked to your account. Please contact the school administration.</p>
            </Card>
          ) : (
            children.map((child) => (
              <Card key={child.id} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[#1c64f2]/20 text-[#7fa5ff] text-xl font-semibold">
                      {child.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'NA'}
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white">{child.full_name}</h3>
                      <p className="text-sm text-[#9eb1cf]">
                        {child.class || child.grade || child.admission_number || child.student_id || "No class assigned"}
                      </p>
                    </div>
                  </div>
                  <Badge tone="good">Active</Badge>
                </div>

                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mt-6">
                  <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <CalendarDays className="h-4 w-4 text-[#d9a441]" />
                      <span className="text-xs uppercase tracking-wider text-[#9eb1cf]">Attendance</span>
                    </div>
                    <p className="text-lg font-semibold text-white">{child.attendance || "95%"}</p>
                  </div>

                  <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="h-4 w-4 text-[#d9a441]" />
                      <span className="text-xs uppercase tracking-wider text-[#9eb1cf]">Behaviour</span>
                    </div>
                    <p className="text-lg font-semibold text-white">{child.behaviour || "Good"}</p>
                  </div>

                  <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertCircle className="h-4 w-4 text-[#d9a441]" />
                      <span className="text-xs uppercase tracking-wider text-[#9eb1cf]">Medical</span>
                    </div>
                    <p className="text-lg font-semibold text-white">{child.medical_flag || "None"}</p>
                  </div>

                  <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="h-4 w-4 text-[#d9a441]" />
                      <span className="text-xs uppercase tracking-wider text-[#9eb1cf]">Fee Status</span>
                    </div>
                    <p className="text-lg font-semibold text-white">{child.fee_status || "Paid"}</p>
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <Button className="flex-1">
                    <BookOpen className="mr-2 h-4 w-4" />
                    View Academic Records
                  </Button>
                  <Button variant="secondary" className="flex-1">
                    <FileText className="mr-2 h-4 w-4" />
                    View Reports
                  </Button>
                </div>
              </Card>
            ))
          )}
        </div>
      )}
    </AppShell>
  );
}

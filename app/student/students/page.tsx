"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { User, CalendarDays, BookOpen, FileText, AlertCircle, GraduationCap } from "lucide-react";
import { getAccessToken, getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface StudentProfile {
  id: string;
  full_name: string;
  email?: string;
  admission_number?: string;
  class?: string;
  grade?: string;
  section?: string;
  date_of_birth?: string;
  gender?: string;
  address?: string;
  phone?: string;
  guardian_name?: string;
  guardian_phone?: string;
}

export default function StudentProfilePage() {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    fetch(`${API_URL}/student/profile`, { headers })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) setProfile(data);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell
      eyebrow="Student Portal"
      title="My Profile"
      description="View and manage your personal information and academic details."
      allowedRoles={["student"]}
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <div className="space-y-6">
          <Card className="p-6">
            <div className="flex items-start gap-6">
              <div className="flex h-24 w-24 items-center justify-center rounded-full bg-[#d9a441]/15 text-[#d9a441] text-3xl font-semibold">
                {profile?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'NA'}
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-semibold text-white">{profile?.full_name || "Student Name"}</h3>
                <p className="text-sm text-[#9eb1cf]">{profile?.email || "No email on record"}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Badge tone="good">Active Student</Badge>
                  <Badge tone="neutral">{profile?.class || profile?.grade || "Not assigned"}</Badge>
                </div>
              </div>
            </div>
          </Card>

          <div className="grid gap-6 md:grid-cols-2">
            <Card className="p-6">
              <h4 className="text-lg font-semibold text-white mb-4">Personal Information</h4>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <User className="h-5 w-5 text-[#d9a441]" />
                  <div>
                    <p className="text-xs text-[#9eb1cf]">Full Name</p>
                    <p className="text-white">{profile?.full_name || "—"}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <CalendarDays className="h-5 w-5 text-[#d9a441]" />
                  <div>
                    <p className="text-xs text-[#9eb1cf]">Date of Birth</p>
                    <p className="text-white">{profile?.date_of_birth || "—"}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <AlertCircle className="h-5 w-5 text-[#d9a441]" />
                  <div>
                    <p className="text-xs text-[#9eb1cf]">Gender</p>
                    <p className="text-white">{profile?.gender || "—"}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-[#d9a441]" />
                  <div>
                    <p className="text-xs text-[#9eb1cf]">Phone</p>
                    <p className="text-white">{profile?.phone || "—"}</p>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h4 className="text-lg font-semibold text-white mb-4">Academic Information</h4>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <GraduationCap className="h-5 w-5 text-[#d9a441]" />
                  <div>
                    <p className="text-xs text-[#9eb1cf]">Admission Number</p>
                    <p className="text-white">{profile?.admission_number || "—"}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <BookOpen className="h-5 w-5 text-[#d9a441]" />
                  <div>
                    <p className="text-xs text-[#9eb1cf]">Class/Grade</p>
                    <p className="text-white">{profile?.class || profile?.grade || "—"}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-[#d9a441]" />
                  <div>
                    <p className="text-xs text-[#9eb1cf]">Section</p>
                    <p className="text-white">{profile?.section || "—"}</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          <Card className="p-6">
            <h4 className="text-lg font-semibold text-white mb-4">Guardian Information</h4>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="text-xs text-[#9eb1cf]">Guardian Name</p>
                <p className="mt-1 text-white">{profile?.guardian_name || "—"}</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="text-xs text-[#9eb1cf]">Guardian Phone</p>
                <p className="mt-1 text-white">{profile?.guardian_phone || "—"}</p>
              </div>
            </div>
          </Card>

          {profile?.address && (
            <Card className="p-6">
              <h4 className="text-lg font-semibold text-white mb-4">Address</h4>
              <p className="text-[#c9d7ef]">{profile.address}</p>
            </Card>
          )}
        </div>
      )}
    </AppShell>
  );
}

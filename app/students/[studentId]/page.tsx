"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useStudentQuery } from "@/hooks/use-crm-query";

export default function StudentDetailPage() {
  const params = useParams();
  const studentId = Array.isArray(params?.studentId) ? params.studentId[0] : params?.studentId ?? "";
  const { data, isLoading } = useStudentQuery(studentId);

  return (
    <AppShell
      eyebrow="Student profile"
      title="Student details"
      description="Review attendance, behaviour, medical and fee status for a single student."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <Card className="space-y-5">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Student</p>
              <p className="mt-2 text-2xl font-semibold text-white">{data.fullName}</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[#9eb1cf]">Class</p>
                <p className="mt-2 text-lg text-white">{data.className}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Guardian</p>
                <p className="mt-2 text-lg text-white">{data.guardian}</p>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <p className="text-sm text-[#9eb1cf]">Attendance</p>
                <p className="mt-2 text-lg text-white">{data.attendance}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Behaviour</p>
                <Badge tone={data.behaviour === "Excellent" ? "good" : data.behaviour === "Good" ? "neutral" : "warn"}>{data.behaviour}</Badge>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Medical flag</p>
                <p className="mt-2 text-lg text-white">{data.medicalFlag}</p>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-[#9eb1cf]">Next assessment</p>
                <p className="mt-2 text-lg text-white">{data.nextAssessment}</p>
              </div>
              <div>
                <p className="text-sm text-[#9eb1cf]">Fee status</p>
                <Badge tone={data.feeStatus === "Paid in full" ? "good" : "warn"}>{data.feeStatus}</Badge>
              </div>
            </div>
            <div>
              <p className="text-sm text-[#9eb1cf]">Documents</p>
              <div className="mt-3 space-y-2">
                {data.documents.map((document) => (
                  <div key={document} className="rounded-[24px] border border-white/10 bg-white/5 px-4 py-3 text-sm text-[#d6dfef]">
                    {document}
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card className="space-y-4">
            <p className="text-sm uppercase tracking-[0.35em] text-[#d9a441]">Student operations</p>
            <p className="text-sm leading-7 text-[#9eb1cf]">
              Use this page to coordinate the student’s attendance, behaviour alerts, medical response, and term fee follow-up.
            </p>
          </Card>
        </div>
      )}
    </AppShell>
  );
}

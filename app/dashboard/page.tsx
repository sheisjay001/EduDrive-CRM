"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { ActionHint, InsightFeed, KpiGrid, LoadingPanel, SectionTitle, TrendPanel } from "@/components/dashboard/ops-primitives";
import { useDashboardQuery } from "@/hooks/use-crm-query";
import { getUser } from "@/services/auth-storage";

export default function DashboardPage() {
  const { data, isLoading } = useDashboardQuery();
  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";

  const getDashboardContent = () => {
    switch (userRole) {
      case "super_admin":
        return {
          eyebrow: "Super Admin Dashboard",
          title: "Multi-School Overview",
          description: "Manage all schools, system-wide operations, and platform administration.",
          kpis: [
            { label: "Total Schools", value: "12", change: "+2 this month", tone: "good" as const },
            { label: "Total Students", value: "4,521", change: "+156 this term", tone: "good" as const },
            { label: "System Revenue", value: "₦2.4M", change: "+18% vs last term", tone: "good" as const },
            { label: "Active Users", value: "89", change: "All systems operational", tone: "neutral" as const },
          ],
        };
      case "admissions_officer":
        return {
          eyebrow: "Admissions Dashboard",
          title: "Lead Management Center",
          description: "Track prospective students, manage tours, and convert leads to enrollments.",
          kpis: [
            { label: "Active Leads", value: "47", change: "+8 this week", tone: "good" as const },
            { label: "Tours Scheduled", value: "12", change: "3 today", tone: "neutral" as const },
            { label: "Conversions", value: "23", change: "+5 this month", tone: "good" as const },
            { label: "Response Rate", value: "78%", change: "+12% improvement", tone: "good" as const },
          ],
        };
      case "bursar":
        return {
          eyebrow: "Finance Dashboard",
          title: "Fee Collections & Payments",
          description: "Monitor invoice status, track payments, and manage school revenue operations.",
          kpis: [
            { label: "Total Revenue", value: "₦1.2M", change: "+18% this term", tone: "good" as const },
            { label: "Outstanding", value: "₦450K", change: "23 invoices pending", tone: "warn" as const },
            { label: "Collection Rate", value: "73%", change: "+5% vs last term", tone: "good" as const },
            { label: "Payments Today", value: "₦85K", change: "12 transactions", tone: "neutral" as const },
          ],
        };
      case "teacher":
        return {
          eyebrow: "Teacher Dashboard",
          title: "Classroom Management",
          description: "Track student attendance, behavior, academic performance, and parent communications.",
          kpis: [
            { label: "My Students", value: "45", change: "JSS 2A • SS 1B", tone: "neutral" as const },
            { label: "Attendance Today", value: "94%", change: "2 absent", tone: "good" as const },
            { label: "Pending Grades", value: "8", change: "Due this week", tone: "warn" as const },
            { label: "Parent Messages", value: "3", change: "Unread", tone: "neutral" as const },
          ],
        };
      case "helpdesk_officer":
        return {
          eyebrow: "Helpdesk Dashboard",
          title: "Support & Ticket Management",
          description: "Track parent inquiries, manage support tickets, and ensure timely resolution of issues.",
          kpis: [
            { label: "Open Tickets", value: "12", change: "3 new today", tone: "neutral" as const },
            { label: "Resolved Today", value: "8", change: "+2 vs yesterday", tone: "good" as const },
            { label: "Avg Response", value: "2.5h", change: "-30min improvement", tone: "good" as const },
            { label: "Escalated", value: "2", change: "Requires attention", tone: "warn" as const },
          ],
        };
      default: // school_admin
        return {
          eyebrow: "School Admin Dashboard",
          title: "School Command Center",
          description: "Track collections, admissions movement, complaints, and operational momentum for the current term.",
          kpis: data?.kpis || [],
        };
    }
  };

  const dashboardContent = getDashboardContent();

  return (
    <AppShell
      eyebrow={dashboardContent.eyebrow}
      title={dashboardContent.title}
      description={dashboardContent.description}
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <KpiGrid items={dashboardContent.kpis} />
          
          {userRole === "school_admin" && (
            <>
              <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
                <Card className="space-y-5">
                  <SectionTitle
                    title="Admissions pipeline"
                    description={`Current school: ${data.schoolName} • ${data.sessionLabel}`}
                    action={<ActionHint text="Move directly into lead follow-up" />}
                  />
                  <div className="grid gap-4 md:grid-cols-2">
                    {data.pipeline.map((stage) => (
                      <div key={stage.stage} className="rounded-[28px] border border-white/10 bg-white/5 p-5">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-lg font-semibold text-white">{stage.stage}</p>
                          <Badge tone="neutral">{stage.count} leads</Badge>
                        </div>
                        <p className="mt-4 font-serif text-4xl text-[#f9d28a]">{stage.value}</p>
                        <p className="mt-3 text-sm text-[#9eb1cf]">{stage.nextAction}</p>
                      </div>
                    ))}
                  </div>
                </Card>

                <InsightFeed items={data.activity} />
              </div>
              <TrendPanel
                title="Weekly collections pulse"
                description="A quick view of how fee recovery is moving through the week."
                data={data.revenueTrend}
                metric="+18% stronger than prior week"
              />
            </>
          )}

          {userRole === "admissions_officer" && (
            <Card className="p-6 mt-6">
              <SectionTitle
                title="Leads by Stage"
                description="Current pipeline status"
              />
              <div className="grid gap-4 mt-4 md:grid-cols-3">
                {data.pipeline.map((stage) => (
                  <div key={stage.stage} className="rounded-xl border border-white/10 bg-white/5 p-5">
                    <div className="flex items-center justify-between">
                      <p className="font-semibold text-white">{stage.stage}</p>
                      <Badge tone="neutral">{stage.count}</Badge>
                    </div>
                    <p className="mt-3 font-serif text-3xl text-[#f9d28a]">{stage.value}</p>
                    <p className="mt-2 text-sm text-[#9eb1cf]">{stage.nextAction}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {userRole === "bursar" && (
            <TrendPanel
              title="Weekly Revenue Trend"
              description="Fee collection performance over the current term"
              data={data.revenueTrend}
              metric="+18% stronger than prior week"
            />
          )}
        </>
      )}
    </AppShell>
  );
}

"use client";

import { Suspense } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Bell,
  BookOpen,
  Bus,
  CalendarCheck,
  ChartSpline,
  CreditCard,
  FileBarChart2,
  FileText,
  GraduationCap,
  LayoutDashboard,
  LifeBuoy,
  LogOut,
  MessageSquareText,
  Settings,
  ShieldCheck,
  Sparkles,
  Ticket,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn, initialsFromName } from "@/lib/utils";
import { clearAuthTokens } from "@/services/auth-storage";
import { getUser } from "@/services/auth-storage";
import { RouteGuard, type UserRole } from "@/components/shell/route-guard";

type NavItem = {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  roles: string[];
};

const STAFF_ROLES: UserRole[] = [
  "super_admin",
  "school_admin",
  "admissions_officer",
  "bursar",
  "teacher",
  "helpdesk_officer",
];

const ALL_ROLES: UserRole[] = [...STAFF_ROLES, "parent", "student"];

const staffNavigation: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["super_admin", "school_admin", "admissions_officer", "bursar", "helpdesk_officer"] },
  { href: "/teacher/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["teacher"] },
  { href: "/admissions", label: "Admissions", icon: ChartSpline, roles: ["super_admin", "school_admin", "admissions_officer"] },
  { href: "/families", label: "Families", icon: Users, roles: ["super_admin", "school_admin"] },
  { href: "/parents", label: "Parents", icon: Sparkles, roles: ["super_admin", "school_admin", "admissions_officer", "helpdesk_officer"] },
  { href: "/teacher/parents", label: "Parents", icon: Sparkles, roles: ["teacher"] },
  { href: "/students", label: "Students", icon: GraduationCap, roles: ["super_admin", "school_admin", "bursar", "parent", "student"] },
  { href: "/teacher/students", label: "Students", icon: GraduationCap, roles: ["teacher"] },
  { href: "/finance", label: "Finance", icon: CreditCard, roles: ["super_admin", "school_admin", "bursar", "parent"] },
  { href: "/messaging", label: "Messaging", icon: MessageSquareText, roles: ["super_admin", "school_admin", "parent", "student"] },
  { href: "/teacher/messaging", label: "Messaging", icon: MessageSquareText, roles: ["teacher"] },
  { href: "/helpdesk", label: "Help Desk", icon: LifeBuoy, roles: ["super_admin", "school_admin", "helpdesk_officer", "parent", "student"] },
  { href: "/staff", label: "Staff", icon: ShieldCheck, roles: ["super_admin", "school_admin"] },
  { href: "/reports", label: "Reports", icon: FileBarChart2, roles: ["super_admin", "school_admin", "student"] },
  { href: "/teacher/reports", label: "Reports", icon: FileBarChart2, roles: ["teacher"] },
  { href: "/settings", label: "Settings", icon: Settings, roles: ["super_admin", "school_admin", "parent"] },
  { href: "/activity", label: "Activity", icon: Sparkles, roles: ["super_admin", "school_admin"] },
  { href: "/analytics", label: "Analytics", icon: ChartSpline, roles: ["super_admin", "school_admin"] },
  { href: "/frontdesk", label: "Frontdesk", icon: LifeBuoy, roles: ["super_admin", "school_admin"] },
  { href: "/reminders", label: "Reminders", icon: CalendarCheck, roles: ["super_admin", "school_admin", "admissions_officer", "bursar", "student"] },
  { href: "/teacher/reminders", label: "Schedule", icon: CalendarCheck, roles: ["teacher"] },
];

const parentNavigation: NavItem[] = [
  { href: "/parent/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["parent"] },
  { href: "/parent/students", label: "My Children", icon: Users, roles: ["parent"] },
  { href: "/parent/finance", label: "Invoices & Payments", icon: CreditCard, roles: ["parent"] },
  { href: "/parent/helpdesk", label: "Support Tickets", icon: Ticket, roles: ["parent"] },
  { href: "/parent/messaging", label: "Messages", icon: MessageSquareText, roles: ["parent"] },
  { href: "/parent/settings/bus-routes", label: "Transport", icon: Bus, roles: ["parent"] },
];

const studentNavigation: NavItem[] = [
  { href: "/student/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["student"] },
  { href: "/student/students", label: "My Profile", icon: Users, roles: ["student"] },
  { href: "/student/helpdesk", label: "Report Issue", icon: Ticket, roles: ["student"] },
  { href: "/student/messaging", label: "Messages", icon: MessageSquareText, roles: ["student"] },
  { href: "/student/reminders", label: "Schedule", icon: CalendarCheck, roles: ["student"] },
  { href: "/student/reports", label: "Results", icon: FileText, roles: ["student"] },
];

function getNavigationForRole(role: string): NavItem[] {
  if (role === "parent") {
    return parentNavigation.filter(item => item.roles.includes(role));
  }
  if (role === "student") {
    return studentNavigation.filter(item => item.roles.includes(role));
  }
  return staffNavigation.filter(item => item.roles.includes(role));
}

type AppShellProps = {
  title: string;
  eyebrow: string;
  description: string;
  children: React.ReactNode;
  allowedRoles?: readonly UserRole[];
};

function AppShellInner({ title, eyebrow, description, children, allowedRoles, user }: AppShellProps & { user: ReturnType<typeof getUser> }) {
  const pathname = usePathname();
  const router = useRouter();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const userName = (user as { fullName?: string })?.fullName || "User";
  const navigation = getNavigationForRole(userRole);

  const handleLogout = () => {
    clearAuthTokens();
    router.push("/login");
  };

  const handleOpenDailyBrief = () => {
    router.push("/activity");
  };

  const handleOpenAlerts = () => {
    router.push("/reminders");
  };

  return (
    <RouteGuard allowedRoles={allowedRoles}>
      <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(217,164,65,0.16),_transparent_22%),linear-gradient(180deg,#14213d_0%,#0b1225_55%,#080d19_100%)] text-[#f6f1e8]">
      <div className="mx-auto grid min-h-screen max-w-[1600px] gap-6 px-4 py-4 lg:grid-cols-[280px_minmax(0,1fr)] lg:px-6">
        <Card className="flex flex-col gap-6 overflow-hidden">
          <div className="rounded-[24px] border border-white/10 bg-white/6 p-5">
            <div className="mb-4 flex items-center justify-between">
              <Badge tone="warn">EduDrive CRM</Badge>
              <Sparkles className="h-4 w-4 text-[#d9a441]" />
            </div>
            <h2 className="font-serif text-2xl text-white">
              {userRole === "parent" ? "Parent Portal" : userRole === "student" ? "Student Portal" : "Greenfield College"}
            </h2>
            <p className="mt-2 text-sm leading-6 text-[#9eb1cf]">
              {userRole === "parent"
                ? "Your children's academic journey and school updates in one place."
                : userRole === "student"
                ? "Track your attendance, assignments, and academic progress."
                : "A modern operations command center for admissions, finance, parent care, and reporting."}
            </p>
          </div>

          <nav className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-2xl border px-4 py-3 text-sm transition-all",
                    active
                      ? "border-[#d9a441]/50 bg-[#d9a441]/10 text-white shadow-[0_14px_30px_rgba(217,164,65,0.14)]"
                      : "border-transparent bg-transparent text-[#9eb1cf] hover:border-white/10 hover:bg-white/6 hover:text-white",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}

            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-3 rounded-2xl border border-transparent bg-transparent px-4 py-3 text-sm text-[#9eb1cf] transition-all hover:border-red-500/30 hover:bg-red-500/10 hover:text-red-400"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </nav>

          <div className="mt-auto rounded-[24px] border border-white/10 bg-[#f6f1e8]/8 p-5">
            <p className="text-xs uppercase tracking-[0.3em] text-[#d9a441]">School Health</p>
            <p className="mt-3 text-sm leading-6 text-[#d6dfef]">
              Payment reminders are driving collections, but transport complaints need closer follow-up today.
            </p>
            <Button onClick={handleOpenDailyBrief} className="mt-4 w-full">Open Daily Brief</Button>
          </div>
        </Card>

        <div className="space-y-6">
          <header className="grid gap-4 rounded-[32px] border border-white/10 bg-white/6 px-6 py-5 shadow-[0_24px_80px_rgba(8,11,23,0.28)] backdrop-blur lg:grid-cols-[minmax(0,1fr)_auto]">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">{eyebrow}</p>
              <h1 className="mt-3 font-serif text-4xl leading-tight text-white">{title}</h1>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-[#c1cee3]">{description}</p>
            </div>

            <div className="flex items-start gap-3">
              <Button onClick={handleOpenAlerts} variant="secondary">
                <Bell className="h-4 w-4" />
                7 alerts
              </Button>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-[#d9a441]/30 bg-[#d9a441]/10 text-sm font-semibold text-white">
                {initialsFromName(userName)}
              </div>
            </div>
          </header>

          {children}
        </div>
      </div>
      </div>
    </RouteGuard>
  );
}

export function AppShell({ title, eyebrow, description, children, allowedRoles = ALL_ROLES }: AppShellProps) {
  const user = getUser();
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-[#0b1225] text-[#f6f1e8]">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-[#d9a441]/30 border-t-[#d9a441]" />
          <p className="text-sm text-[#9eb1cf]">Loading shell…</p>
        </div>
      </div>
    }>
      <AppShellInner title={title} eyebrow={eyebrow} description={description} allowedRoles={allowedRoles} user={user}>
        {children}
      </AppShellInner>
    </Suspense>
  );
}

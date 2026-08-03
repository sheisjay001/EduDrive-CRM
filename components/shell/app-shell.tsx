"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Bell,
  ChartSpline,
  CreditCard,
  FileBarChart2,
  GraduationCap,
  LayoutDashboard,
  LifeBuoy,
  LogOut,
  MessageSquareText,
  Settings,
  ShieldCheck,
  Sparkles,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn, initialsFromName } from "@/lib/utils";
import { clearAuthTokens } from "@/services/auth-storage";

import { getUser } from "@/services/auth-storage";

const allNavigation = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["super_admin", "school_admin", "admissions_officer", "bursar", "teacher", "helpdesk_officer"] },
  { href: "/admissions", label: "Admissions", icon: ChartSpline, roles: ["super_admin", "school_admin", "admissions_officer"] },
  { href: "/families", label: "Families", icon: Users, roles: ["super_admin", "school_admin"] },
  { href: "/parents", label: "Parents", icon: Sparkles, roles: ["super_admin", "school_admin", "admissions_officer", "teacher", "helpdesk_officer"] },
  { href: "/students", label: "Students", icon: GraduationCap, roles: ["super_admin", "school_admin", "bursar", "teacher"] },
  { href: "/finance", label: "Finance", icon: CreditCard, roles: ["super_admin", "school_admin", "bursar"] },
  { href: "/messaging", label: "Messaging", icon: MessageSquareText, roles: ["super_admin", "school_admin"] },
  { href: "/helpdesk", label: "Help Desk", icon: LifeBuoy, roles: ["super_admin", "school_admin", "helpdesk_officer"] },
  { href: "/staff", label: "Staff", icon: ShieldCheck, roles: ["super_admin", "school_admin"] },
  { href: "/reports", label: "Reports", icon: FileBarChart2, roles: ["super_admin", "school_admin"] },
  { href: "/settings", label: "Settings", icon: Settings, roles: ["super_admin", "school_admin"] },
];

function getNavigationForRole(role: string) {
  return allNavigation.filter(item => item.roles.includes(role));
}

type AppShellProps = {
  title: string;
  eyebrow: string;
  description: string;
  children: React.ReactNode;
};

export function AppShell({ title, eyebrow, description, children }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const navigation = getNavigationForRole(userRole);

  const handleLogout = () => {
    clearAuthTokens();
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(217,164,65,0.16),_transparent_22%),linear-gradient(180deg,#14213d_0%,#0b1225_55%,#080d19_100%)] text-[#f6f1e8]">
      <div className="mx-auto grid min-h-screen max-w-[1600px] gap-6 px-4 py-4 lg:grid-cols-[280px_minmax(0,1fr)] lg:px-6">
        <Card className="flex flex-col gap-6 overflow-hidden">
          <div className="rounded-[24px] border border-white/10 bg-white/6 p-5">
            <div className="mb-4 flex items-center justify-between">
              <Badge tone="warn">EduDrive CRM</Badge>
              <Sparkles className="h-4 w-4 text-[#d9a441]" />
            </div>
            <h2 className="font-serif text-2xl text-white">Greenfield College</h2>
            <p className="mt-2 text-sm leading-6 text-[#9eb1cf]">
              A modern operations command center for admissions, finance, parent care, and reporting.
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
            <Button className="mt-4 w-full">Open Daily Brief</Button>
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
              <Button variant="secondary">
                <Bell className="h-4 w-4" />
                7 alerts
              </Button>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-[#d9a441]/30 bg-[#d9a441]/10 text-sm font-semibold text-white">
                {initialsFromName("Joy Auta")}
              </div>
            </div>
          </header>

          {children}
        </div>
      </div>
    </div>
  );
}

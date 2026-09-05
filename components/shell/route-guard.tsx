"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { getAccessToken, getUser } from "@/services/auth-storage";
import { getHomeRouteForRole } from "@/app/login/page";

export type UserRole =
  | "super_admin"
  | "school_admin"
  | "admissions_officer"
  | "bursar"
  | "teacher"
  | "helpdesk_officer"
  | "parent"
  | "student";

const ALL_ROLES: UserRole[] = [
  "super_admin",
  "school_admin",
  "admissions_officer",
  "bursar",
  "teacher",
  "helpdesk_officer",
  "parent",
  "student",
];

export function hasAnyRole(userRole: string, allowedRoles: readonly string[]): boolean {
  if (allowedRoles.length === 0) return true;
  if (userRole === "super_admin") return true;
  return allowedRoles.includes(userRole);
}

export interface RouteGuardProps {
  allowedRoles?: readonly UserRole[];
  children: React.ReactNode;
  fallbackLoginPath?: string;
}

function RouteGuardInner({
  allowedRoles = ALL_ROLES,
  children,
  fallbackLoginPath = "/login",
}: RouteGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [verified] = useState(() => {
    const token = getAccessToken();
    const user = getUser();
    const userRole = (user as { role?: string })?.role || "";
    return Boolean(token) && hasAnyRole(userRole, allowedRoles);
  });

  useEffect(() => {
    const token = getAccessToken();
    const user = getUser();
    const userRole = (user as { role?: string })?.role || "";

    if (!token) {
      const redirect = encodeURIComponent(pathname + (searchParams?.toString() ? `?${searchParams.toString()}` : ""));
      const login =
        allowedRoles.length === 1 && allowedRoles[0] === "parent" ? "/parent-login" :
        allowedRoles.length === 1 && allowedRoles[0] === "student" ? "/student-login" :
        fallbackLoginPath;
      router.replace(`${login}?redirect=${redirect}`);
      return;
    }

    if (!hasAnyRole(userRole, allowedRoles)) {
      const home = userRole ? getHomeRouteForRole(userRole) : fallbackLoginPath;
      router.replace(home);
      return;
    }
  }, [router, pathname, searchParams, allowedRoles, fallbackLoginPath]);

  if (!verified) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0b1225] text-[#f6f1e8]">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-[#d9a441]/30 border-t-[#d9a441]" />
          <p className="text-sm text-[#9eb1cf]">Verifying access…</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export function RouteGuard(props: RouteGuardProps) {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-[#0b1225] text-[#f6f1e8]">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-[#d9a441]/30 border-t-[#d9a441]" />
          <p className="text-sm text-[#9eb1cf]">Verifying access…</p>
        </div>
      </div>
    }>
      <RouteGuardInner {...props} />
    </Suspense>
  );
}

export function withRoleProtection<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  allowedRoles: readonly UserRole[],
) {
  function ProtectedComponent(props: P) {
    return (
      <RouteGuard allowedRoles={allowedRoles}>
        <WrappedComponent {...props} />
      </RouteGuard>
    );
  }
  ProtectedComponent.displayName = `withRoleProtection(${WrappedComponent.displayName || WrappedComponent.name || "Component"})`;
  return ProtectedComponent;
}

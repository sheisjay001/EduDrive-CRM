"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useSchool } from "@/lib/school-context";
import { saveAuthTokens, saveUser, getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export const ROLE_HOME_MAP: Record<string, string> = {
  super_admin: "/dashboard",
  school_admin: "/dashboard",
  admissions_officer: "/admissions-officer/dashboard",
  bursar: "/bursar/dashboard",
  teacher: "/teacher/dashboard",
  helpdesk_officer: "/helpdesk-officer/dashboard",
  parent: "/parent/dashboard",
  student: "/student/dashboard",
};

export function getHomeRouteForRole(role: string): string {
  return ROLE_HOME_MAP[role] || "/dashboard";
}

const SAFE_REDIRECT_RE = /^\/[a-zA-Z0-9\-_/%?=&.]*$/;
function safeRedirect(raw: string | null, fallback: string): string {
  if (!raw) return fallback;
  return SAFE_REDIRECT_RE.test(raw) ? raw : fallback;
}

function LoginPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { schoolSlug, schoolInfo } = useSchool();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (getAccessToken()) {
      const stored = localStorage.getItem("edudrive_user");
      let role = "school_admin";
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (parsed?.role) role = parsed.role;
        } catch { /* noop */ }
      }
      router.replace(getHomeRouteForRole(role));
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Login failed");
      }

      saveAuthTokens(data.access_token, data.refresh_token || "");
      saveUser(data.user);

      const userRole = data.user.role;
      const fallback = getHomeRouteForRole(userRole);
      const requested = searchParams?.get("redirect") || null;
      const redirectPath = safeRedirect(requested, fallback);
      
      router.replace(redirectPath);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          {schoolInfo?.logo_url && (
            <div className="flex justify-center mb-4">
              <img src={schoolInfo.logo_url} alt={schoolInfo.name} className="h-16 w-auto" />
            </div>
          )}
          <CardTitle className="text-2xl font-bold text-center">
            {schoolInfo?.name || "EduDrive CRM"}
          </CardTitle>
          <CardDescription className="text-center">
            Sign in to your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <Input
                id="email"
                type="email"
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && (
              <div className="text-sm text-red-500 bg-red-50 dark:bg-red-900/20 p-3 rounded">
                {error}
              </div>
            )}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Signing in..." : "Sign In"}
            </Button>
          </form>
          <div className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
            <p>Don&apos;t have an account?{" "}
              <a href={schoolSlug ? `/${schoolSlug}/signup` : "/signup"} className="text-blue-600 hover:underline">
                Sign up
              </a>
            </p>
            <p className="mt-2">
              <a href="/parent-login" className="text-blue-600 hover:underline">
                Parent Portal
              </a>
              {" | "}
              <a href="/student-login" className="text-blue-600 hover:underline">
                Student Portal
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-blue-500/30 border-t-blue-500" />
          <p className="text-sm text-gray-500">Loading login…</p>
        </div>
      </div>
    }>
      <LoginPageInner />
    </Suspense>
  );
}

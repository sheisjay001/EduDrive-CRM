"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { saveAuthTokens, saveUser, getAccessToken } from "@/services/auth-storage";
import { getHomeRouteForRole } from "@/app/login/page";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

const SAFE_REDIRECT_RE = /^\/[a-zA-Z0-9\-_/%?=&.]*$/;
function safeRedirect(raw: string | null, fallback: string): string {
  if (!raw) return fallback;
  return SAFE_REDIRECT_RE.test(raw) ? raw : fallback;
}

function ParentLoginPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (getAccessToken()) {
      router.replace("/parent/dashboard");
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/parent-login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Parent login failed");
      }

      saveAuthTokens(data.access_token, data.refresh_token || "");
      saveUser(data.user);

      const fallback = getHomeRouteForRole(data.user.role || "parent");
      const requested = searchParams?.get("redirect") || null;
      const redirectPath = safeRedirect(requested, fallback);
      router.replace(redirectPath);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Parent login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center text-green-700">
            Parent Portal
          </CardTitle>
          <CardDescription className="text-center">
            Sign in to access your children&apos;s information
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
                placeholder="parent@example.com"
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
            <Button type="submit" className="w-full bg-green-600 hover:bg-green-700" disabled={isLoading}>
              {isLoading ? "Signing in..." : "Sign In as Parent"}
            </Button>
          </form>
          <div className="mt-4 text-center text-sm text-gray-600 dark:text-gray-400">
            <p>
              <a href="/login" className="text-green-600 hover:underline">
                Staff Login
              </a>
              {" | "}
              <a href="/student-login" className="text-green-600 hover:underline">
                Student Login
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function ParentLoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800 p-4">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-green-500/30 border-t-green-500" />
          <p className="text-sm text-gray-500">Loading login…</p>
        </div>
      </div>
    }>
      <ParentLoginPageInner />
    </Suspense>
  );
}

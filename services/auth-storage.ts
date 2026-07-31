import { supabase } from "@/lib/supabase";

const ACCESS_TOKEN_KEY = "edudrive_access_token";
const REFRESH_TOKEN_KEY = "edudrive_refresh_token";
const USER_KEY = "edudrive_user";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  // For now, use localStorage directly since getSession is async
  // In a real implementation, you'd want to handle this differently
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  // For now, use localStorage directly since getSession is async
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function saveAuthTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function saveUser(user: Record<string, unknown>): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getUser(): Record<string, unknown> | null {
  if (typeof window === "undefined") {
    return null;
  }

  const userStr = window.localStorage.getItem(USER_KEY);
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
}

export function clearAuthTokens(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
  
  // Also clear Supabase session
  supabase.auth.signOut();
}

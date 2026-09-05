import { supabase } from "@/lib/supabase";

const ACCESS_TOKEN_KEY = "edudrive_access_token";
const REFRESH_TOKEN_KEY = "edudrive_refresh_token";
const USER_KEY = "edudrive_user";

export const AUTH_COOKIES = {
  ACCESS: "edudrive_auth",
  ROLE: "edudrive_role",
  USER: "edudrive_user",
} as const;

function setCookie(name: string, value: string, days = 7): void {
  if (typeof document === "undefined") return;
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  const path = ";path=/";
  const secure = typeof window !== "undefined" && window.location.protocol === "https:"
    ? ";Secure;SameSite=Lax"
    : ";SameSite=Lax";
  document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()}${path}${secure}`;
}

function eraseCookie(name: string): void {
  if (typeof document === "undefined") return;
  document.cookie = `${name}=;Max-Age=-99999999;path=/;SameSite=Lax`;
}

export function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : null;
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function saveAuthTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  setCookie(AUTH_COOKIES.ACCESS, accessToken);
}

export function saveUser(user: Record<string, unknown>): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
  const role = (user as { role?: string }).role || "";
  if (role) {
    setCookie(AUTH_COOKIES.ROLE, role);
  }
  setCookie(AUTH_COOKIES.USER, JSON.stringify(user));
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

  eraseCookie(AUTH_COOKIES.ACCESS);
  eraseCookie(AUTH_COOKIES.ROLE);
  eraseCookie(AUTH_COOKIES.USER);

  supabase.auth.signOut();
}

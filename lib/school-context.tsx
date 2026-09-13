"use client";

import { createContext, useContext, useEffect, useState, useRef } from "react";
import { getUser, getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface SchoolInfo {
  id: string;
  name: string;
  slug: string;
  school_type?: string;
  primary_color?: string;
  status?: string;
  logo_url?: string;
  secondary_color?: string;
  subscription_plan?: string;
}

interface SchoolContextType {
  schoolSlug: string;
  schoolInfo: SchoolInfo | null;
  isLoading: boolean;
  setSchoolSlug: (slug: string) => void;
}

const SchoolContext = createContext<SchoolContextType | undefined>(undefined);

export function SchoolProvider({ children }: { children: React.ReactNode }) {
  const [schoolSlug, setSchoolSlug] = useState("");
  const [schoolInfo, setSchoolInfo] = useState<SchoolInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const isMountedRef = useRef(true);

  const fetchSchoolInfoBySlug = async (slug: string) => {
    if (!isMountedRef.current) return;
    
    try {
      const response = await fetch(`${API_URL}/schools/slug/${slug}`);
      if (response.ok && isMountedRef.current) {
        const data = await response.json();
        setSchoolInfo(data.school);
      }
    } catch (error) {
      console.error("Failed to fetch school info by slug:", error);
    }
  };

  const fetchSchoolInfoById = async (schoolId: string) => {
    if (!isMountedRef.current) return;
    
    const accessToken = getAccessToken();
    try {
      const response = await fetch(`${API_URL}/schools/id/${schoolId}`, {
        headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
      });
      if (response.ok && isMountedRef.current) {
        const data = await response.json();
        setSchoolInfo(data.school);
        if (data.school?.slug) {
          setSchoolSlug(data.school.slug);
        }
      }
    } catch (error) {
      console.error("Failed to fetch school info by id:", error);
    }
  };

  useEffect(() => {
    isMountedRef.current = true;
    
    let resolvedSlug = "";
    let resolvedSchoolId = "";
    
    // 1. Extract school slug from URL path
    const pathParts = typeof window !== "undefined"
      ? window.location.pathname.split("/").filter(Boolean)
      : [];
    const slugFromPath = pathParts[0];
    if (slugFromPath && slugFromPath !== "login" && slugFromPath !== "signup"
        && slugFromPath !== "dashboard" && slugFromPath !== "admissions"
        && slugFromPath !== "finance" && slugFromPath !== "settings"
        && slugFromPath !== "families" && slugFromPath !== "parents"
        && slugFromPath !== "students" && slugFromPath !== "messaging"
        && slugFromPath !== "helpdesk" && slugFromPath !== "staff"
        && slugFromPath !== "reports" && slugFromPath !== "activity"
        && slugFromPath !== "analytics" && slugFromPath !== "frontdesk"
        && slugFromPath !== "reminders" && slugFromPath !== "admissions-officer"
        && slugFromPath !== "bursar" && slugFromPath !== "teacher"
        && slugFromPath !== "helpdesk-officer" && slugFromPath !== "parent"
        && slugFromPath !== "student" && slugFromPath !== "forgot-password"
        && slugFromPath !== "reset-password" && slugFromPath !== "parent-login"
        && slugFromPath !== "student-login") {
      resolvedSlug = slugFromPath;
    }

    // 2. Fallback: extract slug / schoolId from logged-in user auth data
    if (!resolvedSlug && typeof window !== "undefined") {
      const user = getUser();
      if (user) {
        const userWithSchool = user as { schoolSlug?: string; schoolId?: string };
        if (userWithSchool.schoolSlug) {
          resolvedSlug = userWithSchool.schoolSlug;
        } else if (userWithSchool.schoolId) {
          resolvedSchoolId = userWithSchool.schoolId;
        }
      }
    }

    const timeoutIds: number[] = [];
    const setters = () => {
      if (!isMountedRef.current) return;
      if (resolvedSlug) {
        setSchoolSlug(resolvedSlug);
      }
      if (resolvedSchoolId && !resolvedSlug) {
        fetchSchoolInfoById(resolvedSchoolId);
      }
      setTimeout(() => {
        if (isMountedRef.current) {
          setIsLoading(false);
        }
      }, 0);
    };
    timeoutIds.push(window.setTimeout(setters, 0));

    return () => {
      isMountedRef.current = false;
      timeoutIds.forEach((id) => window.clearTimeout(id));
    };
  }, []);

  useEffect(() => {
    if (schoolSlug && isMountedRef.current) {
      fetchSchoolInfoBySlug(schoolSlug);
    }
  }, [schoolSlug]);

  return (
    <SchoolContext.Provider value={{ schoolSlug, schoolInfo, isLoading, setSchoolSlug }}>
      {children}
    </SchoolContext.Provider>
  );
}

export function useSchool() {
  const context = useContext(SchoolContext);
  if (context === undefined) {
    throw new Error("useSchool must be used within a SchoolProvider");
  }
  return context;
}

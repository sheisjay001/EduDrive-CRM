"use client";

import { createContext, useContext, useEffect, useState, useRef } from "react";

interface SchoolInfo {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  primary_color?: string;
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

  const fetchSchoolInfo = async (slug: string) => {
    if (!isMountedRef.current) return;
    
    try {
      const response = await fetch(`/api/v1/schools/slug/${slug}`);
      if (response.ok && isMountedRef.current) {
        const data = await response.json();
        setSchoolInfo(data.school);
      }
    } catch (error) {
      console.error("Failed to fetch school info:", error);
    }
  };

  useEffect(() => {
    isMountedRef.current = true;
    
    // Extract school slug from URL path
    const pathParts = window.location.pathname.split("/").filter(Boolean);
    const slugFromPath = pathParts[0];

    if (slugFromPath && slugFromPath !== "login" && slugFromPath !== "signup") {
      setSchoolSlug(slugFromPath);
    }

    setIsLoading(false);

    return () => {
      isMountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (schoolSlug) {
      fetchSchoolInfo(schoolSlug);
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

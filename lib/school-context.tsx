"use client";

import { createContext, useContext, useEffect, useState } from 'react';

interface SchoolContextType {
  schoolSlug: string | null;
  schoolInfo: SchoolInfo | null;
  isLoading: boolean;
  setSchoolSlug: (slug: string) => void;
}

interface SchoolInfo {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
}

const SchoolContext = createContext<SchoolContextType | undefined>(undefined);

export function SchoolProvider({ children }: { children: React.ReactNode }) {
  const [schoolSlug, setSchoolSlug] = useState<string | null>(null);
  const [schoolInfo, setSchoolInfo] = useState<SchoolInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Extract school slug from URL path
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const slugFromPath = pathParts[0] || null;
    
    if (slugFromPath && slugFromPath !== 'login' && slugFromPath !== 'signup') {
      setSchoolSlug(slugFromPath);
    }
    
    setIsLoading(false);
  }, []);

  useEffect(() => {
    if (schoolSlug) {
      // Fetch school information
      fetchSchoolInfo(schoolSlug);
    }
  }, [schoolSlug]);

  const fetchSchoolInfo = async (slug: string) => {
    try {
      const response = await fetch(`/api/v1/schools/slug/${slug}`);
      if (response.ok) {
        const data = await response.json();
        setSchoolInfo(data.school);
      } else {
        // School not found or inactive
        setSchoolInfo(null);
      }
    } catch (error) {
      console.error('Failed to fetch school info:', error);
      setSchoolInfo(null);
    }
  };

  return (
    <SchoolContext.Provider value={{ schoolSlug, schoolInfo, isLoading, setSchoolSlug }}>
      {children}
    </SchoolContext.Provider>
  );
}

export function useSchool() {
  const context = useContext(SchoolContext);
  if (context === undefined) {
    throw new Error('useSchool must be used within a SchoolProvider');
  }
  return context;
}

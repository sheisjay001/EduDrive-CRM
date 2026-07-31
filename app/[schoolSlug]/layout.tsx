"use client";

import { useSchool } from "@/lib/school-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function SchoolLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { schoolSlug: string };
}) {
  const { schoolInfo, isLoading, setSchoolSlug } = useSchool();
  const router = useRouter();

  useEffect(() => {
    setSchoolSlug(params.schoolSlug);
  }, [params.schoolSlug, setSchoolSlug]);

  useEffect(() => {
    if (!isLoading && !schoolInfo) {
      // School not found or inactive, redirect to main login
      router.push("/login");
    }
  }, [isLoading, schoolInfo, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (!schoolInfo) {
    return null;
  }

  return (
    <div className="min-h-full bg-[#0b1225]">
      {children}
    </div>
  );
}

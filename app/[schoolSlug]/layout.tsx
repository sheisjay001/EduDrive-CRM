"use client";

import { useSchool } from "@/lib/school-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { usePathname } from "next/navigation";

export default function SchoolLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ schoolSlug: string }>;
}) {
  const { schoolInfo, isLoading, setSchoolSlug } = useSchool();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    params.then(({ schoolSlug }) => {
      setSchoolSlug(schoolSlug);
    });
  }, [params, setSchoolSlug]);

  // Skip authentication check for signup page
  const isSignupPage = pathname?.endsWith("/signup");

  useEffect(() => {
    if (!isSignupPage && !isLoading && !schoolInfo) {
      router.push("/login");
    }
  }, [isLoading, schoolInfo, router, isSignupPage]);

  if (isLoading && !isSignupPage) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (!isSignupPage && !schoolInfo) {
    return null;
  }

  return (
    <div className="min-h-full bg-[#0b1225]">
      {children}
    </div>
  );
}

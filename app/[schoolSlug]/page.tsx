"use client";

import { useEffect } from "react";
import { useRouter, useParams } from "next/navigation";

export default function SchoolSlugPage() {
  const router = useRouter();
  const params = useParams();

  useEffect(() => {
    // Redirect to the signup page for this school
    const schoolSlug = params.schoolSlug as string;
    router.replace(`/${schoolSlug}/signup`);
  }, [router, params]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0b1225]">
      <div className="text-white">Redirecting to signup...</div>
    </div>
  );
}

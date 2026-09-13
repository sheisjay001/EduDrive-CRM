"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { User, Mail, Lock, Phone, GraduationCap, Building2 } from "lucide-react";
import { useRouter, useParams } from "next/navigation";
import { useState, Suspense } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useSchool } from "@/lib/school-context";
import { saveAuthTokens, saveUser } from "@/services/auth-storage";

const signupSchema = z.object({
  fullName: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.email("Invalid email address"),
  phone: z.string().min(10, "Phone number must be at least 10 characters"),
  password: z.string().min(6, "Password must be at least 6 characters"),
  confirmPassword: z.string().min(6, "Password must be at least 6 characters"),
  role: z.enum(["teacher", "parent", "student"], {
    message: "Please select a role",
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type SignupValues = z.infer<typeof signupSchema>;

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "https://edudrive-crm-backend.onrender.com/api/v1";

const ROLE_HOME_MAP: Record<string, string> = {
  teacher: "/teacher/dashboard",
  parent: "/parent/dashboard",
  student: "/student/dashboard",
};

function getHomeRouteForRole(role: string): string {
  return ROLE_HOME_MAP[role] || "/dashboard";
}

function SignupForm() {
  const router = useRouter();
  const params = useParams();
  const { schoolSlug, schoolInfo } = useSchool();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const form = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      fullName: "",
      email: "",
      phone: "",
      password: "",
      confirmPassword: "",
      role: "student",
    },
  });

  const selectedRole = form.watch("role");

  const onSubmit = async (values: SignupValues) => {
    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/schools/${schoolSlug}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: values.fullName,
          email: values.email,
          phone: values.phone,
          password: values.password,
          role: values.role,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Registration failed");
      }

      const data = await response.json();

      if (data.access_token && data.user) {
        saveAuthTokens(data.access_token, data.refresh_token || "");
        saveUser(data.user);

        const homeRoute = getHomeRouteForRole(values.role);
        router.push(homeRoute);
      } else {
        router.push("/login");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unable to create account. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (!schoolInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0b1225]">
        <div className="text-white">Loading school information...</div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(217,164,65,0.18),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(11,143,106,0.14),_transparent_30%),linear-gradient(180deg,#14213d_0%,#0b1225_60%,#080d19_100%)] px-4 py-6 lg:px-6">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-4xl items-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full"
        >
          <Card className="rounded-[40px] border-[#d9a441]/18 bg-[linear-gradient(180deg,rgba(14,21,40,0.92),rgba(8,13,25,0.94))] p-8 lg:p-12">
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-2 mb-4">
                <Building2 className="h-6 w-6 text-[#d9a441]" />
                <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">{schoolInfo.name}</p>
              </div>
              <h2 className="font-serif text-4xl text-white">Join Our School</h2>
              <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">
                Create your account to access the school portal
              </p>
            </div>

            <form className="space-y-6" onSubmit={form.handleSubmit(onSubmit)}>
              <div>
                <label className="block text-sm mb-2 text-[#d6dfef]">I am a...</label>
                <div className="grid gap-3 md:grid-cols-3">
                  {[
                    { value: "teacher", icon: GraduationCap, label: "Teacher/Staff" },
                    { value: "parent", icon: User, label: "Parent" },
                    { value: "student", icon: User, label: "Student" },
                  ].map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => form.setValue("role", option.value as any)}
                      className={`flex flex-col items-center gap-2 rounded-2xl border p-4 transition ${
                        selectedRole === option.value
                          ? "border-[#d9a441] bg-[#d9a441]/10"
                          : "border-white/10 bg-white/5 hover:border-white/20"
                      }`}
                    >
                      <option.icon className={`h-5 w-5 ${selectedRole === option.value ? "text-[#d9a441]" : "text-[#9eb1cf]"}`} />
                      <span className={`text-sm ${selectedRole === option.value ? "text-white" : "text-[#9eb1cf]"}`}>
                        {option.label}
                      </span>
                    </button>
                  ))}
                </div>
                <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.role?.message}</span>
              </div>

              <div className="grid gap-6 lg:grid-cols-2">
                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">Full Name</label>
                  <div className="relative">
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9eb1cf]" />
                    <input
                      className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 pl-12 pr-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                      {...form.register("fullName")}
                      placeholder="Enter your full name"
                    />
                  </div>
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.fullName?.message}</span>
                </div>

                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9eb1cf]" />
                    <input
                      type="email"
                      className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 pl-12 pr-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                      {...form.register("email")}
                      placeholder="your@email.com"
                    />
                  </div>
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.email?.message}</span>
                </div>

                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">Phone Number</label>
                  <div className="relative">
                    <Phone className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9eb1cf]" />
                    <input
                      type="tel"
                      className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 pl-12 pr-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                      {...form.register("phone")}
                      placeholder="+234 800 000 0000"
                    />
                  </div>
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.phone?.message}</span>
                </div>

                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9eb1cf]" />
                    <input
                      type="password"
                      className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 pl-12 pr-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                      {...form.register("password")}
                      placeholder="••••••••"
                    />
                  </div>
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.password?.message}</span>
                </div>

                <div className="lg:col-span-2">
                  <label className="block text-sm mb-2 text-[#d6dfef]">Confirm Password</label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9eb1cf]" />
                    <input
                      type="password"
                      className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 pl-12 pr-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                      {...form.register("confirmPassword")}
                      placeholder="••••••••"
                    />
                  </div>
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.confirmPassword?.message}</span>
                </div>
              </div>

              {error ? <p className="text-sm text-rose-200">{error}</p> : null}

              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Creating account..." : "Create Account"}
                <User className="h-4 w-4" />
              </Button>

              <p className="mt-4 text-center text-sm text-[#9eb1cf]">
                Already have an account?{" "}
                <button
                  type="button"
                  className="text-[#d9a441] hover:text-[#d9a441]/80 transition"
                  onClick={() => router.push("/login")}
                >
                  Sign in
                </button>
              </p>
            </form>
          </Card>
        </motion.div>
      </div>
    </main>
  );
}

export default function SchoolSignupPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-[#0b1225] text-white">Loading...</div>}>
      <SignupForm />
    </Suspense>
  );
}

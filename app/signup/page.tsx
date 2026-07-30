"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { ArrowRight, UserPlus } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiClient } from "@/services/api-client";

const signupSchema = z.object({
  fullName: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.email("Invalid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
  confirmPassword: z.string().min(6, "Password must be at least 6 characters"),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type SignupValues = z.infer<typeof signupSchema>;

export default function SignupPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const form = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      fullName: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setSubmitting(true);
    setError(null);

    try {
      await apiClient.signup({
        fullName: values.fullName,
        email: values.email,
        password: values.password,
      });
      router.push("/dashboard");
    } catch (err) {
      setError("Unable to create account. Please try again.");
    } finally {
      setSubmitting(false);
    }
  });

  return (
    <main className="grain min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(217,164,65,0.18),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(11,143,106,0.14),_transparent_30%),linear-gradient(180deg,#14213d_0%,#0b1225_60%,#080d19_100%)] px-4 py-6 lg:px-6">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-md items-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full"
        >
          <Card className="rounded-[40px] border-[#d9a441]/18 bg-[linear-gradient(180deg,rgba(14,21,40,0.92),rgba(8,13,25,0.94))] p-8 lg:p-10">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Sign Up</p>
              <h2 className="mt-4 font-serif text-4xl text-white">Create your account</h2>
              <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">
                Join EduDrive CRM to manage your school operations efficiently.
              </p>
            </div>

            <form className="mt-10 space-y-5" onSubmit={onSubmit}>
              <label className="block text-sm">
                <span className="mb-2 block text-[#d6dfef]">Full Name</span>
                <input
                  className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                  {...form.register("fullName")}
                />
                <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.fullName?.message}</span>
              </label>

              <label className="block text-sm">
                <span className="mb-2 block text-[#d6dfef]">Email</span>
                <input
                  type="email"
                  className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                  {...form.register("email")}
                />
                <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.email?.message}</span>
              </label>

              <label className="block text-sm">
                <span className="mb-2 block text-[#d6dfef]">Password</span>
                <input
                  type="password"
                  className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                  {...form.register("password")}
                />
                <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.password?.message}</span>
              </label>

              <label className="block text-sm">
                <span className="mb-2 block text-[#d6dfef]">Confirm Password</span>
                <input
                  type="password"
                  className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                  {...form.register("confirmPassword")}
                />
                <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.confirmPassword?.message}</span>
              </label>

              {error ? <p className="text-sm text-rose-200">{error}</p> : null}

              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Creating account..." : "Create Account"}
                <UserPlus className="h-4 w-4" />
              </Button>

              <p className="mt-4 text-center text-sm text-[#9eb1cf]">
                Already have an account?{" "}
                <button
                  type="button"
                  className="text-[#d9a441] hover:text-[#d9a441]/80 transition"
                  onClick={() => router.push("/")}
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

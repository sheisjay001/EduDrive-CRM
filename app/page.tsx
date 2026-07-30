"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { ArrowRight, CreditCard, ShieldCheck, UserRoundSearch } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiClient } from "@/services/api-client";

const loginSchema = z.object({
  email: z.email(),
  password: z.string().min(6),
});

type LoginValues = z.infer<typeof loginSchema>;

const highlights = [
  {
    title: "Admissions that convert",
    icon: UserRoundSearch,
    text: "Track every lead from first inquiry to enrollment with reminders, assessment scheduling, and visibility into lost opportunities.",
  },
  {
    title: "Collections with clarity",
    icon: CreditCard,
    text: "Issue invoices, monitor debtors, verify online payments, and give parents cleaner payment communication.",
  },
  {
    title: "Operations with accountability",
    icon: ShieldCheck,
    text: "Centralize tickets, staff activity, parent communication, and reporting inside one school-owned workspace.",
  },
];

export default function Home() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "admin@greenfieldcollege.ng",
      password: "Admin@123",
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setSubmitting(true);
    setError(null);

    try {
      await apiClient.login(values);
      router.push("/dashboard");
    } catch {
      setError("Unable to sign in right now. Please try again.");
    } finally {
      setSubmitting(false);
    }
  });

  return (
    <main className="grain min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(217,164,65,0.18),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(11,143,106,0.14),_transparent_30%),linear-gradient(180deg,#14213d_0%,#0b1225_60%,#080d19_100%)] px-4 py-6 lg:px-6">
      <div className="mx-auto grid max-w-[1600px] gap-6 lg:min-h-[calc(100vh-3rem)] lg:grid-cols-[1.2fr_0.9fr]">
        <motion.section
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
          className="rounded-[40px] border border-white/10 bg-white/6 p-8 shadow-[0_32px_120px_rgba(5,8,18,0.32)] backdrop-blur lg:p-12"
        >
          <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">EduDrive CRM</p>
          <h1 className="mt-6 max-w-3xl font-serif text-5xl leading-tight text-white lg:text-7xl">
            Built for schools that want sharper operations and stronger parent trust.
          </h1>
          <p className="mt-6 max-w-2xl text-sm leading-8 text-[#c3d0e3] lg:text-base">
            One platform for admissions, student records, finance, communication, help desk, staff oversight, and reporting across private Nursery, Primary, and Secondary schools in Nigeria.
          </p>

          <div className="mt-10 grid gap-4 lg:grid-cols-3">
            {highlights.map((item, index) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, y: 18 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.14 * index, duration: 0.45 }}
                  className="rounded-[28px] border border-white/10 bg-[#f6f1e8]/6 p-5"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#d9a441]/12 text-[#f6f1e8]">
                    <Icon className="h-5 w-5 text-[#d9a441]" />
                  </div>
                  <h2 className="mt-5 font-serif text-2xl text-white">{item.title}</h2>
                  <p className="mt-3 text-sm leading-7 text-[#adc0da]">{item.text}</p>
                </motion.div>
              );
            })}
          </div>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="flex items-stretch"
        >
          <Card className="flex w-full flex-col justify-between rounded-[40px] border-[#d9a441]/18 bg-[linear-gradient(180deg,rgba(14,21,40,0.92),rgba(8,13,25,0.94))] p-8 lg:p-10">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">School Sign In</p>
              <h2 className="mt-4 font-serif text-4xl text-white">Start the day with the numbers that matter.</h2>
              <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">
                Demo credentials are prefilled so you can move straight into the product workspace.
              </p>
            </div>

            <form className="mt-10 space-y-5" onSubmit={onSubmit}>
              <label className="block text-sm">
                <span className="mb-2 block text-[#d6dfef]">Work email</span>
                <input
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

              {error ? <p className="text-sm text-rose-200">{error}</p> : null}

              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Signing in..." : "Enter EduDrive"}
                <ArrowRight className="h-4 w-4" />
              </Button>

              <p className="mt-4 text-center text-sm text-[#9eb1cf]">
                Don't have an account?{" "}
                <button
                  type="button"
                  className="text-[#d9a441] hover:text-[#d9a441]/80 transition"
                  onClick={() => router.push("/signup")}
                >
                  Sign up for EduDrive
                </button>
              </p>
            </form>

            <div className="mt-8 rounded-[28px] border border-white/10 bg-white/5 p-5">
              <p className="text-xs uppercase tracking-[0.3em] text-[#d9a441]">Included in the demo</p>
              <p className="mt-3 text-sm leading-7 text-[#c3d0e3]">
                Dashboard, admissions pipeline, student and family records, finance overview, messaging, help desk, staff scorecards, reports, settings, and a FastAPI demo backend.
              </p>
            </div>
          </Card>
        </motion.section>
      </div>
    </main>
  );
}

"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { ArrowRight, Check, CreditCard, ShieldCheck, UserRoundSearch } from "lucide-react";
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

const pricingTiers = [
  {
    name: "Basic",
    price: "₦50,000",
    period: "/month",
    description: "Perfect for growing schools",
    features: [
      "Up to 150 Students",
      "Core CRM & Database",
      "Manual Fee Tracking",
      "SMS Communication",
      "Email Support",
      "Basic Reports",
    ],
    cta: "Get Started",
    popular: false,
  },
  {
    name: "Standard",
    price: "₦80,000",
    period: "/month",
    description: "For schools ready to scale",
    features: [
      "Up to 400 Students",
      "Core CRM & Database",
      "Automated Reminders + Receipts",
      "SMS + WhatsApp Broadcasts",
      "Dedicated Account Specialist",
      "Advanced Analytics",
    ],
    cta: "Get Started",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "₦120,000",
    period: "/month",
    description: "For established institutions",
    features: [
      "Unlimited Students",
      "Core CRM & Database",
      "Full Paystack Gateway Integration",
      "Full WhatsApp API Engine",
      "On-site Staff Training",
      "Priority Support + SLA",
    ],
    cta: "Contact Sales",
    popular: false,
  },
];

export default function Home() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLogin, setShowLogin] = useState(false);
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
      const response = await apiClient.login(values);
      
      console.log("Login response:", response);
      console.log("User role:", response.user.role);
      
      const role = response.user.role;
      const dashboardPath = getDashboardPath(role);
      console.log("Redirecting to:", dashboardPath);
      router.push(dashboardPath);
    } catch {
      setError("Unable to sign in right now. Please try again.");
    } finally {
      setSubmitting(false);
    }
  });

  function getDashboardPath(role: string): string {
    const rolePaths: Record<string, string> = {
      super_admin: "/dashboard",
      school_admin: "/dashboard",
      admissions_officer: "/dashboard",
      bursar: "/dashboard",
      teacher: "/dashboard",
      helpdesk_officer: "/dashboard",
    };
    return rolePaths[role] || "/dashboard";
  }

  if (showLogin) {
    return (
      <main className="grain min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(217,164,65,0.18),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(11,143,106,0.14),_transparent_30%),linear-gradient(180deg,#14213d_0%,#0b1225_60%,#080d19_100%)] px-4 py-6 lg:px-6">
        <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-md items-center">
          <motion.section
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="rounded-[40px] border-[#d9a441]/18 bg-[linear-gradient(180deg,rgba(14,21,40,0.92),rgba(8,13,25,0.94))] p-8 lg:p-10">
              <button
                onClick={() => setShowLogin(false)}
                className="mb-4 text-sm text-[#d9a441] hover:text-[#d9a441]/80"
              >
                ← Back to Home
              </button>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">School Sign In</p>
              <h2 className="mt-4 font-serif text-4xl text-white">Welcome back</h2>
              
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
              </form>
            </Card>
          </motion.section>
        </div>
      </main>
    );
  }

  return (
    <main className="grain min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(217,164,65,0.18),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(11,143,106,0.14),_transparent_30%),linear-gradient(180deg,#14213d_0%,#0b1225_60%,#080d19_100%)] px-4 py-6 lg:px-6">
      <div className="mx-auto max-w-[1600px]">
        <motion.section
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
          className="rounded-[40px] border border-white/10 bg-white/6 p-8 shadow-[0_32px_120px_rgba(5,8,18,0.32)] backdrop-blur lg:p-12 mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">EduDrive CRM</p>
              <h1 className="mt-6 max-w-3xl font-serif text-5xl leading-tight text-white lg:text-7xl">
                Built for schools that want sharper operations and stronger parent trust.
              </h1>
              <p className="mt-3 text-sm leading-7 text-[#c3d0e3]">
                One platform for admissions, student records, finance, communication, help desk, staff oversight, and reporting across private Nursery, Primary, and Secondary schools in Nigeria.
              </p>
            </div>
            <div className="hidden lg:flex gap-4">
              <Button
                variant="outline"
                onClick={() => setShowLogin(true)}
                className="rounded-2xl border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"
              >
                Sign In
              </Button>
              <Button
                onClick={() => router.push("/signup")}
                className="rounded-2xl bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
              >
                Register Your School
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

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
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.2 }}
          className="rounded-[40px] border border-white/10 bg-white/6 p-8 shadow-[0_32px_120px_rgba(5,8,18,0.32)] backdrop-blur lg:p-12 mb-8"
        >
          <div className="text-center mb-12">
            <h2 className="font-serif text-4xl text-white lg:text-5xl">Simple, Transparent Pricing</h2>
            <p className="mt-4 text-sm leading-7 text-[#c3d0e3]">
              Choose the plan that fits your school&apos;s size and needs
            </p>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            {pricingTiers.map((tier, index) => (
              <motion.div
                key={tier.name}
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index, duration: 0.45 }}
                className={`rounded-[28px] border p-6 ${
                  tier.popular
                    ? "border-[#d9a441] bg-[#d9a441]/10 shadow-[0_0_40px_rgba(217,164,65,0.2)]"
                    : "border-white/10 bg-white/6"
                }`}
              >
                {tier.popular && (
                  <div className="mb-4 inline-block rounded-full bg-[#d9a441] px-3 py-1 text-xs font-medium text-white">
                    Most Popular
                  </div>
                )}
                <h3 className="font-serif text-2xl text-white">{tier.name}</h3>
                <p className="mt-2 text-sm text-[#adc0da]">{tier.description}</p>
                <div className="mt-6">
                  <span className="text-4xl font-bold text-white">{tier.price}</span>
                  <span className="text-sm text-[#adc0da]">{tier.period}</span>
                </div>
                <ul className="mt-8 space-y-4">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm text-[#c3d0e3]">
                      <Check className="h-5 w-5 flex-shrink-0 text-[#d9a441]" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  onClick={() => router.push("/signup")}
                  className={`mt-8 w-full ${
                    tier.popular
                      ? "bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
                      : "border border-[#d9a441]/30 bg-[#d9a441]/10 text-[#d9a441] hover:bg-[#d9a441]/20"
                  }`}
                >
                  {tier.cta}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </motion.div>
            ))}
          </div>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.3 }}
          className="rounded-[40px] border border-white/10 bg-white/6 p-8 shadow-[0_32px_120px_rgba(5,8,18,0.32)] backdrop-blur lg:p-12 text-center"
        >
          <h2 className="font-serif text-3xl text-white lg:text-4xl">Ready to transform your school operations?</h2>
          <p className="mt-4 text-sm leading-7 text-[#c3d0e3]">
            Join hundreds of schools already using EduDrive to streamline their operations
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={() => router.push("/signup")}
              className="rounded-2xl bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
            >
              Register Your School
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowLogin(true)}
              className="rounded-2xl border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"
            >
              Sign In
            </Button>
          </div>
        </motion.section>
      </div>
    </main>
  );
}

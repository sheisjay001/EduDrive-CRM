"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { ArrowRight, UserPlus, Building2, Check } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const signupSchema = z.object({
  schoolName: z.string().min(2, "School name must be at least 2 characters"),
  fullName: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.email("Invalid email address"),
  phone: z.string().min(10, "Phone number must be at least 10 characters"),
  password: z.string().min(6, "Password must be at least 6 characters"),
  confirmPassword: z.string().min(6, "Password must be at least 6 characters"),
  subscriptionPlan: z.enum(["basic", "standard", "enterprise"]),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type SignupValues = z.infer<typeof signupSchema>;

const pricingPlans = [
  {
    id: "basic",
    name: "Basic",
    price: "₦50,000",
    features: ["Up to 150 Students", "Manual Fee Tracking", "SMS Only", "Email Support"],
  },
  {
    id: "standard",
    name: "Standard",
    price: "₦80,000",
    features: ["Up to 400 Students", "Automated Reminders", "SMS + WhatsApp", "Dedicated Support"],
    popular: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "₦120,000",
    features: ["Unlimited Students", "Full Payment Gateway", "Full WhatsApp API", "On-site Training"],
  },
];

export default function SignupPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);
  const form = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      schoolName: "",
      fullName: "",
      email: "",
      phone: "",
      password: "",
      confirmPassword: "",
      subscriptionPlan: "standard",
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setSubmitting(true);
    setError(null);

    try {
      // Call school registration API
      const response = await fetch("/api/v1/schools/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          school_name: values.schoolName,
          admin_name: values.fullName,
          email: values.email,
          phone: values.phone,
          password: values.password,
          subscription_plan: values.subscriptionPlan,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Registration failed");
      }

      const data = await response.json();
      
      // Store tokens
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      // Redirect to dashboard
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Unable to create account. Please try again.");
    } finally {
      setSubmitting(false);
    }
  });

  const selectedPlan = form.watch("subscriptionPlan");

  return (
    <main className="grain min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(217,164,65,0.18),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(11,143,106,0.14),_transparent_30%),linear-gradient(180deg,#14213d_0%,#0b1225_60%,#080d19_100%)] px-4 py-6 lg:px-6">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-4xl items-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full"
        >
          <Card className="rounded-[40px] border-[#d9a441]/18 bg-[linear-gradient(180deg,rgba(14,21,40,0.92),rgba(8,13,25,0.94))] p-8 lg:p-12">
            <div className="text-center mb-8">
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">School Registration</p>
              <h2 className="mt-4 font-serif text-4xl text-white">Register Your School</h2>
              <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">
                Get your unique school login link and start managing operations efficiently.
              </p>
            </div>

            <form className="space-y-6" onSubmit={onSubmit}>
              <div className="grid gap-6 lg:grid-cols-2">
                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">School Name</label>
                  <input
                    className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                    {...form.register("schoolName")}
                    placeholder="e.g., Greenfield College"
                  />
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.schoolName?.message}</span>
                </div>

                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">Your Full Name</label>
                  <input
                    className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                    {...form.register("fullName")}
                    placeholder="Admin name"
                  />
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.fullName?.message}</span>
                </div>

                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">Email Address</label>
                  <input
                    type="email"
                    className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                    {...form.register("email")}
                    placeholder="admin@school.ng"
                  />
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.email?.message}</span>
                </div>

                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">Phone Number</label>
                  <input
                    type="tel"
                    className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                    {...form.register("phone")}
                    placeholder="+234 800 000 0000"
                  />
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.phone?.message}</span>
                </div>

                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">Password</label>
                  <input
                    type="password"
                    className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                    {...form.register("password")}
                  />
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.password?.message}</span>
                </div>

                <div>
                  <label className="block text-sm mb-2 text-[#d6dfef]">Confirm Password</label>
                  <input
                    type="password"
                    className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                    {...form.register("confirmPassword")}
                  />
                  <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.confirmPassword?.message}</span>
                </div>
              </div>

              <div>
                <label className="block text-sm mb-4 text-[#d6dfef]">Select Subscription Plan</label>
                <div className="grid gap-4 lg:grid-cols-3">
                  {pricingPlans.map((plan) => (
                    <div
                      key={plan.id}
                      onClick={() => form.setValue("subscriptionPlan", plan.id as any)}
                      className={`cursor-pointer rounded-2xl border p-4 transition ${
                        selectedPlan === plan.id
                          ? "border-[#d9a441] bg-[#d9a441]/10"
                          : "border-white/10 bg-white/6 hover:border-white/20"
                      }`}
                    >
                      {plan.popular && (
                        <div className="mb-2 inline-block rounded-full bg-[#d9a441] px-2 py-0.5 text-xs font-medium text-white">
                          Popular
                        </div>
                      )}
                      <h3 className="font-serif text-lg text-white">{plan.name}</h3>
                      <p className="text-2xl font-bold text-[#d9a441]">{plan.price}<span className="text-sm text-[#adc0da]">/mo</span></p>
                      <ul className="mt-3 space-y-2">
                        {plan.features.map((feature) => (
                          <li key={feature} className="flex items-start gap-2 text-xs text-[#c3d0e3]">
                            <Check className="h-4 w-4 flex-shrink-0 text-[#d9a441]" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {error ? <p className="text-sm text-rose-200">{error}</p> : null}

              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Creating account..." : "Register School"}
                <Building2 className="h-4 w-4" />
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

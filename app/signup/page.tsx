"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Building2, Calculator } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect, Suspense } from "react";
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
  studentCount: z.number().min(0, "Student count must be at least 0"),
  teacherCount: z.number().min(0, "Teacher count must be at least 0"),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
}).refine((data) => data.studentCount > 0 || data.teacherCount > 0, {
  message: "At least one student or teacher must be added",
  path: ["studentCount"],
});

type SignupValues = z.infer<typeof signupSchema>;

const PRICE_PER_PERSON = 1000; // 1,000 NGN per person

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

function SignupForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentStep, setPaymentStep] = useState(false);
  const [paymentReference, setPaymentReference] = useState<string | null>(null);
  const form = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      schoolName: "",
      fullName: "",
      email: "",
      phone: "",
      password: "",
      confirmPassword: "",
      studentCount: 0,
      teacherCount: 0,
    },
  });

  const studentCount = form.watch("studentCount");
  const teacherCount = form.watch("teacherCount");
  const totalPersons = studentCount + teacherCount;
  const totalAmount = totalPersons * PRICE_PER_PERSON;

  // Check if payment reference is in URL (callback from Paystack)
  useEffect(() => {
    const reference = searchParams.get("reference");
    if (reference) {
      setPaymentReference(reference);
      setPaymentStep(true);
      
      // Retrieve form data from sessionStorage
      if (typeof window !== "undefined") {
        const storedData = sessionStorage.getItem("registrationFormData");
        if (storedData) {
          const formData = JSON.parse(storedData);
          form.reset(formData);
          sessionStorage.removeItem("registrationFormData");
          
          // Auto-submit registration after a short delay
          setTimeout(() => {
            completeRegistration();
          }, 500);
        }
      }
    }
  }, [searchParams]);

  const initializePayment = async () => {
    setSubmitting(true);
    setError(null);

    try {
      const formData = {
        schoolName: form.getValues("schoolName"),
        fullName: form.getValues("fullName"),
        email: form.getValues("email"),
        phone: form.getValues("phone"),
        password: form.getValues("password"),
        confirmPassword: form.getValues("confirmPassword"),
        studentCount,
        teacherCount,
      };
      
      // Store form data in sessionStorage for retrieval after payment
      if (typeof window !== "undefined") {
        sessionStorage.setItem("registrationFormData", JSON.stringify(formData));
      }
      
      const response = await fetch(`${API_URL}/schools/payments/initialize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.getValues("email"),
          student_count: studentCount,
          teacher_count: teacherCount,
          payment_method: "paystack",
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Payment initialization failed");
      }

      const data = await response.json();
      
      // Redirect to Paystack payment page
      if (data.data?.authorization_url) {
        window.location.href = data.data.authorization_url;
      } else {
        throw new Error("Invalid payment response");
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unable to initialize payment. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const completeRegistration = async () => {
    if (!paymentReference) return;

    setSubmitting(true);
    setError(null);

    try {
      console.log("Starting registration with payment reference:", paymentReference);
      
      const response = await fetch(`${API_URL}/schools/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          school_name: form.getValues("schoolName"),
          admin_name: form.getValues("fullName"),
          email: form.getValues("email"),
          phone: form.getValues("phone"),
          password: form.getValues("password"),
          student_count: studentCount,
          teacher_count: teacherCount,
          payment_method: "paystack",
          payment_reference: paymentReference,
        }),
      });

      console.log("Registration response status:", response.status);

      if (!response.ok) {
        const data = await response.json();
        console.error("Registration failed:", data);
        throw new Error(data.detail || "Registration failed");
      }

      console.log("Registration successful, redirecting to login");
      // Redirect to login page
      router.push("/login");
    } catch (err: unknown) {
      console.error("Registration error:", err);
      setError(err instanceof Error ? err.message : "Unable to create account. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const onSubmit = paymentStep ? completeRegistration : initializePayment;

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
              <h2 className="mt-4 font-serif text-4xl text-white">{paymentStep ? "Complete Registration" : "Register Your School"}</h2>
              <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">
                {paymentStep 
                  ? "Payment successful! Complete your school registration."
                  : "Get your unique school login link and start managing operations efficiently."
                }
              </p>
            </div>

            <form className="space-y-6" onSubmit={form.handleSubmit(onSubmit)}>
              {!paymentStep && (
                <>
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
                    <label className="block text-sm mb-4 text-[#d6dfef]">Number of Students & Teachers</label>
                    <div className="grid gap-4 lg:grid-cols-2">
                      <div>
                        <label className="block text-xs mb-2 text-[#9eb1cf]">Students</label>
                        <input
                          type="number"
                          min="0"
                          className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                          {...form.register("studentCount", { valueAsNumber: true })}
                          placeholder="0"
                        />
                        <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.studentCount?.message}</span>
                      </div>

                      <div>
                        <label className="block text-xs mb-2 text-[#9eb1cf]">Teachers</label>
                        <input
                          type="number"
                          min="0"
                          className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                          {...form.register("teacherCount", { valueAsNumber: true })}
                          placeholder="0"
                        />
                        <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.teacherCount?.message}</span>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-[#d9a441]/30 bg-[#d9a441]/10 p-4">
                    <div className="flex items-center gap-3">
                      <Calculator className="h-5 w-5 text-[#d9a441]" />
                      <div className="flex-1">
                        <p className="text-sm text-[#d6dfef]">Total Amount</p>
                        <p className="text-2xl font-bold text-[#d9a441]">
                          ₦{totalAmount.toLocaleString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-[#9eb1cf]">{totalPersons} persons</p>
                        <p className="text-xs text-[#9eb1cf]">@ ₦{PRICE_PER_PERSON.toLocaleString()}/person</p>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {error ? <p className="text-sm text-rose-200">{error}</p> : null}

              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting 
                  ? (paymentStep ? "Creating account..." : "Processing payment...")
                  : (paymentStep ? "Complete Registration" : `Pay ₦${totalAmount.toLocaleString()} & Register`)
                }
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

export default function SignupPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SignupForm />
    </Suspense>
  );
}

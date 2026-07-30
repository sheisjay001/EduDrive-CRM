"use client";

import Link from "next/link";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiClient } from "@/services/api-client";

const forgotPasswordSchema = z.object({
  email: z.string().email(),
});

type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const form = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setError(null);
    try {
      const response = await apiClient.forgotPassword(values);
      setMessage(response.message);
      setSubmitted(true);
    } catch {
      setError("We could not send the reset link right now. Try again later.");
    }
  });

  return (
    <main className="flex min-h-screen items-center justify-center bg-[linear-gradient(180deg,#14213d_0%,#080d19_100%)] px-4 py-10">
      <Card className="w-full max-w-xl rounded-[36px] p-10">
        <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Password Recovery</p>
        <h1 className="mt-4 font-serif text-4xl text-white">Reset your staff password</h1>
        <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">
          Enter the account email and we’ll send a secure reset link. For the demo, you can proceed to the reset page directly.
        </p>

        {submitted && message ? (
          <div className="mt-8 rounded-[28px] border border-white/10 bg-white/5 p-6 text-sm text-[#d6dfef]">
            <p className="font-semibold text-white">{message}</p>
            <p className="mt-3">Continue to the reset page to complete the flow.</p>
            <div className="mt-5 flex flex-wrap gap-3">
              <Link href="/reset-password">
                <Button>Complete reset</Button>
              </Link>
              <Link href="/">
                <Button variant="secondary">Back to sign in</Button>
              </Link>
            </div>
          </div>
        ) : (
          <form className="mt-8 space-y-5" onSubmit={onSubmit}>
            <label className="block text-sm">
              <span className="mb-2 block text-[#d6dfef]">Email address</span>
              <input
                className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                {...form.register("email")}
              />
              <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.email?.message}</span>
            </label>

            {error ? <p className="text-sm text-rose-200">{error}</p> : null}

            <Button type="submit" className="w-full">
              Send reset link
            </Button>
            <div className="text-sm text-[#9eb1cf]">
              Already have a token? <Link href="/reset-password" className="text-[#d9a441] underline">Use it here.</Link>
            </div>
          </form>
        )}
      </Card>
    </main>
  );
}

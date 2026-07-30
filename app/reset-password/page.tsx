"use client";

import Link from "next/link";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiClient } from "@/services/api-client";

const resetPasswordSchema = z.object({
  token: z.string().min(1, "Token is required"),
  newPassword: z.string().min(6, "Password must be at least 6 characters"),
});

type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>;

export default function ResetPasswordPage() {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const form = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { token: "", newPassword: "" },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    setError(null);
    try {
      const response = await apiClient.resetPassword(values);
      setMessage(response.message);
    } catch {
      setError("Unable to complete password reset. Please check your token and try again.");
    }
  });

  return (
    <main className="flex min-h-screen items-center justify-center bg-[linear-gradient(180deg,#14213d_0%,#080d19_100%)] px-4 py-10">
      <Card className="w-full max-w-xl rounded-[36px] p-10">
        <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Reset Password</p>
        <h1 className="mt-4 font-serif text-4xl text-white">Set a new staff password</h1>
        <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">
          Enter the reset token from your email and choose a new secure password for the account.
        </p>

        {message ? (
          <div className="mt-8 rounded-[28px] border border-white/10 bg-white/5 p-6 text-sm text-[#d6dfef]">
            <p className="font-semibold text-white">{message}</p>
            <div className="mt-5 flex flex-wrap gap-3">
              <Link href="/">
                <Button>Back to sign in</Button>
              </Link>
            </div>
          </div>
        ) : (
          <form className="mt-8 space-y-5" onSubmit={onSubmit}>
            <label className="block text-sm">
              <span className="mb-2 block text-[#d6dfef]">Reset token</span>
              <input
                className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                {...form.register("token")}
              />
              <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.token?.message}</span>
            </label>

            <label className="block text-sm">
              <span className="mb-2 block text-[#d6dfef]">New password</span>
              <input
                type="password"
                className="h-13 w-full rounded-2xl border border-white/10 bg-white/6 px-4 text-sm text-white outline-none transition focus:border-[#d9a441]"
                {...form.register("newPassword")}
              />
              <span className="mt-2 block text-xs text-rose-200">{form.formState.errors.newPassword?.message}</span>
            </label>

            {error ? <p className="text-sm text-rose-200">{error}</p> : null}

            <Button type="submit" className="w-full">
              Reset password
            </Button>

            <div className="text-sm text-[#9eb1cf]">
              Remembered your password? <Link href="/" className="text-[#d9a441] underline">Sign in</Link>
            </div>
          </form>
        )}
      </Card>
    </main>
  );
}

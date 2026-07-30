import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const toneStyles = {
  neutral: "bg-white/8 text-[#cdd8eb]",
  good: "bg-emerald-500/15 text-emerald-200",
  warn: "bg-amber-500/15 text-amber-200",
  danger: "bg-rose-500/15 text-rose-200",
} as const;

export function Badge({
  className,
  tone = "neutral",
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: keyof typeof toneStyles }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium",
        toneStyles[tone],
        className,
      )}
      {...props}
    />
  );
}

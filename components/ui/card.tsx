import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-[28px] border border-white/10 bg-[rgba(15,23,42,0.75)] p-6 shadow-[0_24px_80px_rgba(7,10,22,0.35)] backdrop-blur",
        className,
      )}
      {...props}
    />
  );
}

"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useSettingsQuery } from "@/hooks/use-crm-query";

export default function SettingsPage() {
  const { data, isLoading } = useSettingsQuery();

  return (
    <AppShell
      eyebrow="School Settings"
      title="Brand, billing, and channel configuration"
      description="Set the school’s identity, payment providers, sender profiles, and academic structure from a configuration space built for administrators."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 xl:grid-cols-3">
          {data.groups.map((group) => (
            <Card key={group.title}>
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">{group.title}</p>
              <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">{group.description}</p>
              <div className="mt-6 space-y-4">
                {group.items.map((item) => (
                  <div key={item.label} className="rounded-[24px] border border-white/10 bg-white/5 p-4">
                    <p className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">{item.label}</p>
                    <p className="mt-2 text-sm font-medium text-white">{item.value}</p>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}

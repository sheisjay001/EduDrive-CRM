"use client";

import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useMessageTemplatesQuery } from "@/hooks/use-crm-query";

export default function MessageTemplatesPage() {
  const { data, isLoading } = useMessageTemplatesQuery();

  return (
    <AppShell
      eyebrow="Message templates"
      title="Reusable communication assets"
      description="Manage the reusable templates that power announcements, reminders, receipts, and support notifications."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          {data.templates.map((template: any) => (
            <Card key={template.id} className="space-y-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm text-[#9eb1cf]">{template.channel}</p>
                  <p className="mt-2 text-2xl font-semibold text-white">{template.name}</p>
                </div>
                <Badge tone="neutral">{template.useCase}</Badge>
              </div>
              <p className="text-sm leading-7 text-[#d6dfef]">Last edited {template.lastEdited}.</p>
              <div className="text-sm text-[#9eb1cf]">
                <Link href="#" className="text-[#d9a441] underline">
                  Preview template
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}

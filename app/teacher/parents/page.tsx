"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Users, MessageSquare, Phone, Mail, CalendarCheck } from "lucide-react";

export default function TeacherParentsPage() {
  return (
    <AppShell
      eyebrow="Teacher Portal"
      title="Parent Communications"
      description="View parent contacts and communication history for your students."
      allowedRoles={["teacher"]}
    >
      <div className="space-y-4">
        {[
          { parent: "Mrs. Doe", student: "John Doe", class: "JSS 2A", lastContact: "2 days ago", unread: 2 },
          { parent: "Mr. Smith", student: "Jane Smith", class: "JSS 2A", lastContact: "1 week ago", unread: 0 },
          { parent: "Mrs. Brown", student: "Michael Brown", class: "JSS 2A", lastContact: "3 days ago", unread: 1 },
          { parent: "Mr. Johnson", student: "Sarah Johnson", class: "JSS 2A", lastContact: "Today", unread: 3 },
        ].map((item, idx) => (
          <Card key={idx} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                  <Users className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">{item.parent}</h3>
                  <p className="text-sm text-[#9eb1cf]">Parent of {item.student} • {item.class}</p>
                </div>
              </div>
              {item.unread > 0 && (
                <Badge tone="warn">{item.unread} unread</Badge>
              )}
            </div>
            <div className="grid gap-3 md:grid-cols-3 text-sm">
              <div className="flex items-center gap-2 text-[#9eb1cf]">
                <Phone className="h-4 w-4" />
                +234 801 234 5678
              </div>
              <div className="flex items-center gap-2 text-[#9eb1cf]">
                <Mail className="h-4 w-4" />
                parent@example.com
              </div>
              <div className="flex items-center gap-2 text-[#9eb1cf]">
                <CalendarCheck className="h-4 w-4" />
                Last contact: {item.lastContact}
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              <button className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-[#d9a441]/30 bg-[#d9a441]/10 px-4 py-2 text-sm text-white transition-all hover:bg-[#d9a441]/20">
                <MessageSquare className="h-4 w-4" />
                Send Message
              </button>
              <button className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition-all hover:bg-white/10">
                View History
              </button>
            </div>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}

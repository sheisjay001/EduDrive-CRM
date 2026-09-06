"use client";

import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { MessageSquare, Bell, Clock, Send, Users } from "lucide-react";
import { useState } from "react";

export default function TeacherMessagingPage() {
  const [selectedMessage, setSelectedMessage] = useState<number | null>(null);

  const messages = [
    { id: 1, from: "Mrs. Doe", subject: "John's progress", preview: "I wanted to discuss John's recent performance in Mathematics...", time: "2 hours ago", unread: true },
    { id: 2, from: "Mr. Smith", subject: "Assignment clarification", preview: "Could you please explain the homework assignment...", time: "Yesterday", unread: true },
    { id: 3, from: "School Admin", subject: "Staff meeting reminder", preview: "Don't forget about the staff meeting tomorrow...", time: "2 days ago", unread: false },
    { id: 4, from: "Mrs. Brown", subject: "Attendance concern", preview: "I noticed Michael was marked absent...", time: "3 days ago", unread: true },
  ];

  return (
    <AppShell
      eyebrow="Teacher Portal"
      title="Messages"
      description="Communicate with parents, students, and school administration."
      allowedRoles={["teacher"]}
    >
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-1">
          <h3 className="text-lg font-semibold text-white mb-4">Inbox</h3>
          <div className="space-y-2">
            {messages.map((msg) => (
              <div
                key={msg.id}
                onClick={() => setSelectedMessage(msg.id)}
                className={`cursor-pointer rounded-xl border p-4 transition-all ${
                  selectedMessage === msg.id
                    ? "border-[#d9a441]/50 bg-[#d9a441]/10"
                    : msg.unread
                    ? "border-white/20 bg-white/5"
                    : "border-transparent bg-transparent"
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                    <Users className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-white text-sm">{msg.from}</p>
                      {msg.unread && <div className="h-2 w-2 rounded-full bg-[#d9a441]" />}
                    </div>
                    <p className="text-xs text-white mt-1 truncate">{msg.subject}</p>
                    <p className="text-xs text-[#9eb1cf] mt-1">{msg.time}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6 lg:col-span-2">
          {selectedMessage ? (
            <div>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-white">
                    {messages.find(m => m.id === selectedMessage)?.subject}
                  </h3>
                  <p className="text-sm text-[#9eb1cf]">
                    From: {messages.find(m => m.id === selectedMessage)?.from}
                  </p>
                </div>
                <Badge tone="neutral">
                  {messages.find(m => m.id === selectedMessage)?.time}
                </Badge>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-4 mb-4">
                <p className="text-[#c9d7ef]">
                  {messages.find(m => m.id === selectedMessage)?.preview}
                  This is a sample message content. In a real application, this would contain the full message text.
                </p>
              </div>
              <div className="flex gap-2">
                <button className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-[#d9a441]/30 bg-[#d9a441]/10 px-4 py-2 text-sm text-white transition-all hover:bg-[#d9a441]/20">
                  <Send className="h-4 w-4" />
                  Reply
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition-all hover:bg-white/10">
                  Forward
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <MessageSquare className="h-16 w-16 text-[#9eb1cf] mb-4" />
              <h3 className="text-lg font-semibold text-white mb-2">Select a Message</h3>
              <p className="text-[#9eb1cf]">Choose a message from the inbox to view its contents.</p>
            </div>
          )}
        </Card>
      </div>
    </AppShell>
  );
}

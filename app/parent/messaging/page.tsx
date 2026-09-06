"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { MessageSquare, Bell, Clock, Mail, Send } from "lucide-react";
import { getAccessToken, getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Message {
  id: string;
  subject?: string;
  body?: string;
  sent_at?: string;
  channel?: string;
  sender?: string;
}

export default function ParentMessagingPage() {
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    fetch(`${API_URL}/parent/communications`, { headers })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) setMessages(data.communications || data.messages || []);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell
      eyebrow="Parent Portal"
      title="Messages"
      description="View communications and announcements from the school administration."
      allowedRoles={["parent"]}
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <div className="space-y-4">
          {messages.length === 0 ? (
            <Card className="p-12 text-center">
              <MessageSquare className="h-16 w-16 mx-auto text-[#9eb1cf] mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Messages</h3>
              <p className="text-[#9eb1cf]">You haven't received any messages from the school yet.</p>
            </Card>
          ) : (
            messages.map((msg) => (
              <Card key={msg.id} className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                      <Bell className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{msg.subject || "School Announcement"}</h3>
                      <p className="text-sm text-[#9eb1cf]">From: {msg.sender || "School Administration"}</p>
                    </div>
                  </div>
                  {msg.channel && (
                    <Badge tone="neutral">{msg.channel}</Badge>
                  )}
                </div>
                <p className="text-sm text-[#c9d7ef] mb-4">{msg.body || "No content available."}</p>
                <div className="flex items-center gap-4 text-sm text-[#9eb1cf]">
                  {msg.sent_at && (
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {msg.sent_at}
                    </div>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      )}
    </AppShell>
  );
}

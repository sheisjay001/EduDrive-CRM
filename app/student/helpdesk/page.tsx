"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Ticket, Plus, MessageSquare, Clock, CheckCircle, AlertCircle } from "lucide-react";
import { getAccessToken, getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Ticket {
  id: string;
  subject: string;
  description?: string;
  status: string;
  priority: string;
  created_at?: string;
  updated_at?: string;
}

export default function StudentHelpdeskPage() {
  const [loading, setLoading] = useState(true);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [addFormData, setAddFormData] = useState({ subject: "", description: "" });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    fetch(`${API_URL}/student/tickets`, { headers })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) setTickets(data.tickets || data || []);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const handleAddTicket = async () => {
    if (!addFormData.subject) {
      alert("Please enter a subject");
      return;
    }
    try {
      const token = getAccessToken();
      const response = await fetch(`${API_URL}/student/tickets`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(addFormData),
      });
      if (response.ok) {
        setShowAddForm(false);
        setAddFormData({ subject: "", description: "" });
        // Refetch tickets
        const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
        fetch(`${API_URL}/student/tickets`, { headers })
          .then(r => r.ok ? r.json() : null)
          .then(data => {
            if (data) setTickets(data.tickets || data || []);
          });
        alert("Ticket created successfully");
      } else {
        alert("Failed to create ticket");
      }
    } catch (error) {
      alert("Error creating ticket");
    }
  };

  return (
    <AppShell
      eyebrow="Student Portal"
      title="Report Issue"
      description="Submit and track support requests for school-related issues."
      allowedRoles={["student"]}
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <>
          <div className="mb-6">
            {!showAddForm ? (
              <Button onClick={() => setShowAddForm(true)} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
                <Plus className="h-4 w-4 mr-2" />
                New Ticket
              </Button>
            ) : (
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Create New Ticket</h3>
                <div className="space-y-4">
                  <input
                    type="text"
                    placeholder="Subject"
                    value={addFormData.subject}
                    onChange={(e) => setAddFormData({ ...addFormData, subject: e.target.value })}
                    className="w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                  />
                  <textarea
                    placeholder="Description"
                    value={addFormData.description}
                    onChange={(e) => setAddFormData({ ...addFormData, description: e.target.value })}
                    rows={4}
                    className="w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                  />
                  <div className="flex gap-2">
                    <Button onClick={handleAddTicket} className="bg-green-600 text-white hover:bg-green-700">
                      Submit Ticket
                    </Button>
                    <Button onClick={() => setShowAddForm(false)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                      Cancel
                    </Button>
                  </div>
                </div>
              </Card>
            )}
          </div>

          <div className="space-y-4">
            {tickets.length === 0 ? (
              <Card className="p-12 text-center">
                <Ticket className="h-16 w-16 mx-auto text-[#9eb1cf] mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No Tickets</h3>
                <p className="text-[#9eb1cf]">You haven't submitted any support tickets yet.</p>
              </Card>
            ) : (
              tickets.map((ticket) => (
                <Card key={ticket.id} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                        <Ticket className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-white">{ticket.subject}</h3>
                        <p className="text-sm text-[#9eb1cf]">#{ticket.id}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Badge tone={ticket.status === "Resolved" ? "good" : ticket.status === "In Progress" ? "warn" : "neutral"}>
                        {ticket.status}
                      </Badge>
                      <Badge tone={ticket.priority === "Urgent" ? "danger" : ticket.priority === "High" ? "warn" : "neutral"}>
                        {ticket.priority}
                      </Badge>
                    </div>
                  </div>
                  {ticket.description && (
                    <p className="text-sm text-[#c9d7ef] mb-4">{ticket.description}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-[#9eb1cf]">
                    {ticket.created_at && (
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        Created: {ticket.created_at}
                      </div>
                    )}
                    {ticket.updated_at && (
                      <div className="flex items-center gap-1">
                        <MessageSquare className="h-4 w-4" />
                        Updated: {ticket.updated_at}
                      </div>
                    )}
                  </div>
                </Card>
              ))
            )}
          </div>
        </>
      )}
    </AppShell>
  );
}

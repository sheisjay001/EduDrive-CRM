"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { Plus, Calendar, CheckCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function TermsPage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [terms, setTerms] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateSessionDialog, setShowCreateSessionDialog] = useState(false);
  const [showCreateTermDialog, setShowCreateTermDialog] = useState(false);

  const fetchTerms = async () => {
    try {
      const response = await fetch(`${API_URL}/settings/terms`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setTerms(Array.isArray(data) ? data : data.terms || []);
      }
    } catch (error) {
      console.error("Error fetching terms:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useState(() => {
    fetchTerms();
  });

  const handleCreateSession = async (sessionData: Record<string, unknown>) => {
    try {
      const response = await fetch(`${API_URL}/terms/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(sessionData),
      });

      if (response.ok) {
        setShowCreateSessionDialog(false);
        fetchTerms();
      }
    } catch (error) {
      console.error("Error creating session:", error);
    }
  };

  const handleCreateTerm = async (termData: Record<string, unknown>) => {
    try {
      const response = await fetch(`${API_URL}/terms/terms`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(termData),
      });

      if (response.ok) {
        setShowCreateTermDialog(false);
        fetchTerms();
      }
    } catch (error) {
      console.error("Error creating term:", error);
    }
  };

  const handleSetActiveTerm = async (termId: string) => {
    try {
      const response = await fetch(`${API_URL}/terms/terms/${termId}/set-current`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.ok) {
        fetchTerms();
      }
    } catch (error) {
      console.error("Error setting active term:", error);
    }
  };

  return (
    <AppShell
      eyebrow="Academic Calendar"
      title="Term and session management"
      description="Configure academic sessions, terms, and important dates for the school year."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button variant="secondary">
                <Calendar className="mr-2 h-4 w-4" />
                Sessions ({sessions.length})
              </Button>
              <Button variant="secondary">
                <CheckCircle className="mr-2 h-4 w-4" />
                Terms ({terms.length})
              </Button>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => setShowCreateTermDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Term
              </Button>
              <Button onClick={() => setShowCreateSessionDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Session
              </Button>
            </div>
          </div>

          <div className="space-y-6">
            {terms.length === 0 ? (
              <Card className="p-6">
                <p className="text-center text-[#9eb1cf]">No academic terms configured</p>
              </Card>
            ) : (
              terms.map((term) => (
                <Card key={term.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-white">{term.name}</h3>
                        {term.is_active && (
                          <Badge className="bg-green-500/20 text-green-400">
                            <CheckCircle className="mr-1 h-3 w-3" />
                            Active
                          </Badge>
                        )}
                        <Badge variant="outline" className="border-[#d9a441]/30 text-[#d9a441]">
                          {term.session_name}
                        </Badge>
                      </div>
                      <div className="mt-3 flex items-center gap-4 text-sm text-[#9eb1cf]">
                        <span className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          {new Date(term.start_date).toLocaleDateString()} - {new Date(term.end_date).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="mt-4">
                        <p className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Important Dates</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {term.important_dates?.map((date: any) => (
                            <Badge key={date.id} variant="outline" className="border-white/20 text-white">
                              {date.title}: {new Date(date.date).toLocaleDateString()}
                            </Badge>
                          )) || <span className="text-sm text-[#9eb1cf]">No important dates set</span>}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {!term.is_active && (
                        <Button
                          size="sm"
                          onClick={() => handleSetActiveTerm(term.id)}
                          variant="outline"
                          className="border-green-500/30 text-green-500 hover:bg-green-500/10"
                        >
                          Set Active
                        </Button>
                      )}
                      <Button size="sm" variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                        Edit
                      </Button>
                      <Button size="sm" variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                        Delete
                      </Button>
                    </div>
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

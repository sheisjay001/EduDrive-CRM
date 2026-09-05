"use client";

import { useState, useEffect, useCallback } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Calendar, CheckCircle } from "lucide-react";
import { getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Term {
  id: string;
  term_name: string;
  term_code: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  is_active: boolean;
  important_dates?: Array<{ id: string; title: string; date: string }>;
}

export default function TermsPage() {
  const [terms, setTerms] = useState<Term[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTerms = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/settings/terms`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTerms(Array.isArray(data) ? data : data.terms || []);
      }
    } catch {
      console.error("Error fetching terms");
    } finally {
      setIsLoading(false);
    }
  }, []);

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    fetchTerms();
  }, [fetchTerms]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const handleSetActiveTerm = async (termId: string) => {
    try {
      const response = await fetch(`${API_URL}/terms/terms/${termId}/set-current`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });

      if (response.ok) {
        fetchTerms();
      }
    } catch {
      console.error("Error setting active term");
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
                Terms ({terms.length})
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
                        <h3 className="text-lg font-semibold text-white">{term.term_name}</h3>
                        {term.is_active && (
                          <Badge className="bg-green-500/20 text-green-400">
                            <CheckCircle className="mr-1 h-3 w-3" />
                            Active
                          </Badge>
                        )}
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
                          {term.important_dates?.map((date) => (
                            <Badge key={date.id} className="border-white/20 text-white">
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
                      <Button size="sm" variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10" onClick={() => confirm("Edit term feature coming soon")}>
                        Edit
                      </Button>
                      <Button size="sm" variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10" onClick={() => confirm("Delete term feature coming soon")}>
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

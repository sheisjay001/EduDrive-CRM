"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { FileText, Award, TrendingUp, Calendar, BookOpen, Download } from "lucide-react";
import { getAccessToken, getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Result {
  id: string;
  subject?: string;
  term?: string;
  score?: number;
  grade?: string;
  total?: number;
  date?: string;
}

export default function StudentReportsPage() {
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState<Result[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    fetch(`${API_URL}/student/results`, { headers })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) setResults(data.results || data || []);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  const averageScore = results.length > 0 
    ? Math.round(results.reduce((sum, r) => sum + (r.score || 0), 0) / results.length)
    : 0;

  return (
    <AppShell
      eyebrow="Student Portal"
      title="Results"
      description="View your academic results, grades, and performance reports."
      allowedRoles={["student"]}
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                  <Award className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs text-[#9eb1cf]">Average Score</p>
                  <p className="text-2xl font-semibold text-white">{averageScore}%</p>
                </div>
              </div>
            </Card>
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/20 text-green-400">
                  <TrendingUp className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs text-[#9eb1cf]">Total Subjects</p>
                  <p className="text-2xl font-semibold text-white">{results.length}</p>
                </div>
              </div>
            </Card>
            <Card className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500/20 text-purple-400">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs text-[#9eb1cf]">Current Term</p>
                  <p className="text-2xl font-semibold text-white">{results[0]?.term || "—"}</p>
                </div>
              </div>
            </Card>
          </div>

          <Card className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Subject Results</h3>
            {results.length === 0 ? (
              <p className="text-[#9eb1cf]">No results available yet.</p>
            ) : (
              <div className="space-y-4">
                {results.map((result) => (
                  <div key={result.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                          <BookOpen className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="font-semibold text-white">{result.subject || "Subject"}</p>
                          <p className="text-sm text-[#9eb1cf]">{result.term || "—"}</p>
                        </div>
                      </div>
                      <Badge tone={
                        (result.score || 0) >= 70 ? "good" :
                        (result.score || 0) >= 50 ? "warn" : "danger"
                      }>
                        {result.grade || "—"}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-sm text-[#9eb1cf]">
                        {result.date && (
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            {result.date}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-white">{result.score || 0}/{result.total || 100}</p>
                      </div>
                    </div>
                    <div className="mt-3 h-2 w-full rounded-full bg-white/10 overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${
                          (result.score || 0) >= 70 ? "bg-green-500" :
                          (result.score || 0) >= 50 ? "bg-[#d9a441]" : "bg-red-500"
                        }`}
                        style={{ width: `${((result.score || 0) / (result.total || 100)) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Download Reports</h3>
            <div className="grid gap-3 md:grid-cols-2">
              <Button variant="secondary" className="justify-start">
                <Download className="mr-2 h-4 w-4" />
                Download Result Sheet
              </Button>
              <Button variant="secondary" className="justify-start">
                <Download className="mr-2 h-4 w-4" />
                Download Transcript
              </Button>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}

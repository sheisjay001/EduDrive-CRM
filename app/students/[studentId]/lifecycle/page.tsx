"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { BookOpen, AlertTriangle, Activity, Calendar } from "lucide-react";
import { getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface LifecycleLog {
  id: string;
  log_type: string;
  description: string;
  created_at: string;
  term?: string;
  title?: string;
  resolved_at?: string;
}

export default function StudentLifecyclePage() {
  const { studentId } = useParams();
  const [lifecycleLogs, setLifecycleLogs] = useState<LifecycleLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"all" | "academic" | "disciplinary" | "medical" | "attendance">("all");

  const fetchLifecycleLogs = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/lifecycle/logs/student/${studentId}`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setLifecycleLogs(Array.isArray(data) ? data : data.logs || []);
      }
    } catch (error) {
      console.error("Error fetching lifecycle logs:", error);
    } finally {
      setIsLoading(false);
    }
  }, [studentId]);

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    fetchLifecycleLogs();
  }, [fetchLifecycleLogs]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const getLogTypeIcon = (type: string) => {
    const icons: Record<string, typeof BookOpen> = {
      academic: BookOpen,
      disciplinary: AlertTriangle,
      medical: Activity,
      attendance: Calendar,
    };
    return icons[type] || BookOpen;
  };

  const getLogTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      academic: "bg-blue-500/20 text-blue-400",
      disciplinary: "bg-red-500/20 text-red-400",
      medical: "bg-green-500/20 text-green-400",
      attendance: "bg-yellow-500/20 text-yellow-400",
    };
    return colors[type] || "bg-gray-500/20 text-gray-400";
  };

  const filteredLogs = activeTab === "all" 
    ? lifecycleLogs 
    : lifecycleLogs.filter(log => log.log_type === activeTab);

  return (
    <AppShell
      eyebrow="Student Lifecycle"
      title="Complete student history and records"
      description="Track academic performance, disciplinary records, medical history, and attendance throughout the student's journey."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button
                variant={activeTab === "all" ? "primary" : "secondary"}
                onClick={() => setActiveTab("all")}
              >
                All Records
              </Button>
              <Button
                variant={activeTab === "academic" ? "primary" : "secondary"}
                onClick={() => setActiveTab("academic")}
              >
                <BookOpen className="mr-2 h-4 w-4" />
                Academic
              </Button>
              <Button
                variant={activeTab === "disciplinary" ? "primary" : "secondary"}
                onClick={() => setActiveTab("disciplinary")}
              >
                <AlertTriangle className="mr-2 h-4 w-4" />
                Disciplinary
              </Button>
              <Button
                variant={activeTab === "medical" ? "primary" : "secondary"}
                onClick={() => setActiveTab("medical")}
              >
                <Activity className="mr-2 h-4 w-4" />
                Medical
              </Button>
              <Button
                variant={activeTab === "attendance" ? "primary" : "secondary"}
                onClick={() => setActiveTab("attendance")}
              >
                <Calendar className="mr-2 h-4 w-4" />
                Attendance
              </Button>
            </div>
          </div>

          <Card className="p-6">
            <SectionTitle 
              title="Lifecycle Timeline" 
              description="Student records and history" 
            />
            
            <div className="mt-6 space-y-4">
              {filteredLogs.length === 0 ? (
                <p className="text-center text-[#9eb1cf]">No records found</p>
              ) : (
                filteredLogs.map((log) => {
                  const Icon = getLogTypeIcon(log.log_type);
                  return (
                    <div
                      key={log.id}
                      className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-4"
                    >
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20">
                        <Icon className="h-5 w-5 text-[#d9a441]" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <Badge className={getLogTypeColor(log.log_type)}>
                            {log.log_type}
                          </Badge>
                          <span className="text-sm text-[#9eb1cf]">
                            {new Date(log.created_at).toLocaleString()}
                          </span>
                          {log.term && (
                            <Badge className="border-[#d9a441]/30 text-[#d9a441]">
                              {log.term}
                            </Badge>
                          )}
                        </div>
                        <p className="mt-2 font-medium text-white">{log.title}</p>
                        <p className="mt-1 text-sm text-[#9eb1cf]">{log.description}</p>
                        {log.resolved_at && (
                          <p className="mt-1 text-xs text-green-400">
                            Resolved: {new Date(log.resolved_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </Card>
        </>
      )}
    </AppShell>
  );
}

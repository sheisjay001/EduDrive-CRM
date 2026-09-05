"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { User, TrendingUp, AlertCircle, CheckCircle } from "lucide-react";
import { getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface WorkloadData {
  total_staff: number;
  average_workload: number;
  overloaded_staff: number;
  underutilized_staff: number;
  optimal_count?: number;
  high_count?: number;
  overloaded_count?: number;
  staff_workload?: Array<{ id: string; name: string; workload: number; priority: string; role?: string; workload_percentage?: number; task_count?: number }>;
}

interface RoleSummary {
  role: string;
  count: number;
  average_workload: number;
  staff_count?: number;
  avg_workload?: number;
  total_tasks?: number;
  productivity_score?: number;
  priority_level?: string;
}

interface PerformanceTrends {
  labels: string[];
  workload: number[];
  efficiency: number[];
  monthly_trends?: Array<{ month: string; avg_workload: number; efficiency: number; productivity?: number; improvement?: number; change?: number }>;
}

export default function WorkloadPage() {
  const [workloadData, setWorkloadData] = useState<WorkloadData | null>(null);
  const [roleSummary, setRoleSummary] = useState<RoleSummary[]>([]);
  const [performanceTrends, setPerformanceTrends] = useState<PerformanceTrends | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"current" | "by-role" | "trends">("current");

  const fetchCurrentWorkload = async () => {
    try {
      const response = await fetch(`${API_URL}/workload/current`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setWorkloadData(data);
      }
    } catch (error) {
      console.error("Error fetching workload:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRoleSummary = async () => {
    try {
      const response = await fetch(`${API_URL}/workload/summary-by-role`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setRoleSummary(Array.isArray(data) ? data : data.roles || []);
      }
    } catch (error) {
      console.error("Error fetching role summary:", error);
    }
  };

  const fetchPerformanceTrends = async () => {
    try {
      const response = await fetch(`${API_URL}/workload/performance-trends`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setPerformanceTrends(data);
      }
    } catch (error) {
      console.error("Error fetching performance trends:", error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      if (activeTab === "current") await fetchCurrentWorkload();
      else if (activeTab === "by-role") await fetchRoleSummary();
      else if (activeTab === "trends") await fetchPerformanceTrends();
    };
    loadData();
  }, [activeTab]);

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      low: "bg-green-500/20 text-green-400",
      normal: "bg-blue-500/20 text-blue-400",
      high: "bg-yellow-500/20 text-yellow-400",
      overloaded: "bg-red-500/20 text-red-400",
    };
    return colors[priority] || "bg-gray-500/20 text-gray-400";
  };

  const getPriorityIcon = (priority: string) => {
    const icons: Record<string, typeof CheckCircle> = {
      low: CheckCircle,
      normal: CheckCircle,
      high: AlertCircle,
      overloaded: AlertCircle,
    };
    return icons[priority] || CheckCircle;
  };

  return (
    <AppShell
      eyebrow="Staff Workload Management"
      title="Monitor and optimize staff productivity"
      description="Track staff workload, productivity metrics, and performance trends to ensure balanced resource allocation."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button
                variant={activeTab === "current" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("current"); fetchCurrentWorkload(); }}
              >
                Current Workload
              </Button>
              <Button
                variant={activeTab === "by-role" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("by-role"); fetchRoleSummary(); }}
              >
                By Role
              </Button>
              <Button
                variant={activeTab === "trends" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("trends"); fetchPerformanceTrends(); }}
              >
                <TrendingUp className="mr-2 h-4 w-4" />
                Trends
              </Button>
            </div>
            <Button variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
              Update Workload
            </Button>
          </div>

          {activeTab === "current" && (
            <div className="space-y-6">
              <div className="grid gap-4 xl:grid-cols-4">
                <Card className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/20">
                      <CheckCircle className="h-5 w-5 text-green-400" />
                    </div>
                    <div>
                      <p className="text-sm text-[#9eb1cf]">Optimal Load</p>
                      <p className="text-2xl font-bold text-white">{workloadData?.optimal_count || "0"}</p>
                    </div>
                  </div>
                </Card>
                <Card className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-500/20">
                      <AlertCircle className="h-5 w-5 text-yellow-400" />
                    </div>
                    <div>
                      <p className="text-sm text-[#9eb1cf]">High Load</p>
                      <p className="text-2xl font-bold text-white">{workloadData?.high_count || "0"}</p>
                    </div>
                  </div>
                </Card>
                <Card className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-500/20">
                      <AlertCircle className="h-5 w-5 text-red-400" />
                    </div>
                    <div>
                      <p className="text-sm text-[#9eb1cf]">Overloaded</p>
                      <p className="text-2xl font-bold text-white">{workloadData?.overloaded_count || "0"}</p>
                    </div>
                  </div>
                </Card>
                <Card className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500/20">
                      <User className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm text-[#9eb1cf]">Total Staff</p>
                      <p className="text-2xl font-bold text-white">{workloadData?.total_staff || "0"}</p>
                    </div>
                  </div>
                </Card>
              </div>

              <Card className="p-6">
                <SectionTitle 
                  title="Individual Workload" 
                  description="Current workload status by staff member" 
                />
                <div className="mt-4 space-y-4">
                  {workloadData?.staff_workload?.map((staff) => {
                    const PriorityIcon = getPriorityIcon(staff.priority);
                    return (
                      <div key={staff.id} className="flex items-start justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                        <div className="flex items-center gap-4">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20">
                            <User className="h-5 w-5 text-[#d9a441]" />
                          </div>
                          <div>
                            <p className="font-medium text-white">{staff.name}</p>
                            <p className="text-sm text-[#9eb1cf]">{staff.role}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <p className="text-sm font-medium text-white">{staff.workload_percentage}%</p>
                            <p className="text-xs text-[#9eb1cf]">{staff.task_count} tasks</p>
                          </div>
                          <Badge className={getPriorityColor(staff.priority)}>
                            <PriorityIcon className="mr-1 h-3 w-3" />
                            {staff.priority}
                          </Badge>
                        </div>
                      </div>
                    );
                  }) || <p className="text-center text-[#9eb1cf]">No workload data available</p>}
                </div>
              </Card>
            </div>
          )}

          {activeTab === "by-role" && (
            <Card className="p-6">
              <SectionTitle 
                title="Workload by Role" 
                description="Aggregate workload metrics by staff role" 
              />
              <div className="mt-4 space-y-4">
                {roleSummary.length === 0 ? (
                  <p className="text-center text-[#9eb1cf]">No role data available</p>
                ) : (
                  roleSummary.map((role) => (
                    <div key={role.role} className="flex items-start justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold text-white">{role.role}</h3>
                          <Badge className="border-[#d9a441]/30 text-[#d9a441]">
                            {role.staff_count} staff
                          </Badge>
                        </div>
                        <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-[#9eb1cf]">Avg Workload</p>
                            <p className="font-medium text-white">{role.avg_workload}%</p>
                          </div>
                          <div>
                            <p className="text-[#9eb1cf]">Total Tasks</p>
                            <p className="font-medium text-white">{role.total_tasks}</p>
                          </div>
                          <div>
                            <p className="text-[#9eb1cf]">Productivity</p>
                            <p className="font-medium text-white">{role.productivity_score}</p>
                          </div>
                        </div>
                      </div>
                      <Badge className={getPriorityColor(role.priority_level || "medium")}>
                        {role.priority_level || "Medium"}
                      </Badge>
                    </div>
                  ))
                )}
              </div>
            </Card>
          )}

          {activeTab === "trends" && (
            <Card className="p-6">
              <SectionTitle 
                title="Performance Trends" 
                description="Workload and productivity trends over time" 
              />
              <div className="mt-4 space-y-4">
                {performanceTrends?.monthly_trends?.map((trend) => (
                  <div key={trend.month} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <p className="font-medium text-white">{trend.month}</p>
                      <p className="text-sm text-[#9eb1cf]">Avg Workload: {trend.avg_workload}%</p>
                    </div>
                    <div className="flex gap-4 text-sm">
                      <span className="text-[#9eb1cf]">Productivity: {trend.productivity}</span>
                      <Badge className={trend.improvement ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"}>
                        {trend.improvement ? "+" : "-"}{trend.change}%
                      </Badge>
                    </div>
                  </div>
                )) || <p className="text-center text-[#9eb1cf]">No trend data available</p>}
              </div>
            </Card>
          )}
        </>
      )}
    </AppShell>
  );
}

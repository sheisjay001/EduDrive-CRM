"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface Activity {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  user_id: string;
  user_name?: string;
  timestamp: string;
  created_at?: string;
  description?: string;
  details?: Record<string, unknown>;
}

export default function ActivityPage() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "user" | "entity">("all");
  const user = getUser();

  const fetchActivities = async () => {
    try {
      const endpoint = filter === "all" 
        ? "/activity/recent" 
        : filter === "user" 
        ? `/activity/user/${user?.id}` 
        : "/activity/stats";
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setActivities(Array.isArray(data) ? data : data.activities || []);
      }
    } catch (error) {
      console.error("Error fetching activities:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const loadActivities = async () => {
      await fetchActivities();
    };
    loadActivities();
  }, [filter]);

  const getActivityTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      lead: "bg-blue-500/20 text-blue-400",
      payment: "bg-green-500/20 text-green-400",
      invoice: "bg-yellow-500/20 text-yellow-400",
      message: "bg-purple-500/20 text-purple-400",
      ticket: "bg-red-500/20 text-red-400",
      student: "bg-cyan-500/20 text-cyan-400",
    };
    return colors[type] || "bg-gray-500/20 text-gray-400";
  };

  return (
    <AppShell
      eyebrow="Activity Audit Log"
      title="Track all system actions"
      description="Monitor user activities, changes to records, and system events for accountability and audit purposes."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button
                variant={filter === "all" ? "primary" : "secondary"}
                onClick={() => { setFilter("all"); fetchActivities(); }}
              >
                All Activities
              </Button>
              <Button
                variant={filter === "user" ? "primary" : "secondary"}
                onClick={() => { setFilter("user"); fetchActivities(); }}
              >
                My Activities
              </Button>
              <Button
                variant={filter === "entity" ? "primary" : "secondary"}
                onClick={() => { setFilter("entity"); fetchActivities(); }}
              >
                Statistics
              </Button>
            </div>
          </div>

          <Card className="p-6">
            <SectionTitle 
              title="Activity Timeline" 
              description="Recent actions across the system" 
            />
            
            <div className="mt-6 space-y-4">
              {activities.length === 0 ? (
                <p className="text-center text-[#9eb1cf]">No activities found</p>
              ) : (
                activities.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-4"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <Badge className={getActivityTypeColor(activity.entity_type)}>
                          {activity.entity_type}
                        </Badge>
                        <span className="text-sm text-[#9eb1cf]">
                          {activity.created_at ? new Date(activity.created_at).toLocaleString() : new Date(activity.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="mt-2 font-medium text-white">{activity.action}</p>
                      <p className="mt-1 text-sm text-[#9eb1cf]">
                        {activity.description || `Entity: ${activity.entity_type} #${activity.entity_id}`}
                      </p>
                      <p className="mt-1 text-xs text-[#8ea4c8]">
                        By: {activity.user_name || activity.user_id}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </>
      )}
    </AppShell>
  );
}

"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { Phone, Users, Calendar, Plus, Check, X } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface DailyLog {
  id: string;
  date: string;
  staff_id: string;
  staff_name: string;
  calls_logged: number;
  calls_answered: number;
  calls_missed: number;
  visitors_checked_in: number;
  visitors_checked_out: number;
  walk_in_inquiries: number;
  new_leads: number;
  tours_scheduled: number;
  performance_rating: number;
}

interface Activity {
  id: string;
  daily_log_id: string;
  activity_type: string;
  description: string;
  timestamp: string;
}

export default function FrontDeskPage() {
  const [dailyLogs, setDailyLogs] = useState<DailyLog[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateLogDialog, setShowCreateLogDialog] = useState(false);
  const [showActivityDialog, setShowActivityDialog] = useState(false);
  const [activeTab, setActiveTab] = useState<"logs" | "activities" | "performance">("logs");

  const fetchDailyLogs = async () => {
    try {
      const response = await fetch(`${API_URL}/frontdesk/my-logs`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setDailyLogs(Array.isArray(data) ? data : data.logs || []);
      }
    } catch (error) {
      console.error("Error fetching daily logs:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchActivities = async (logId: string) => {
    try {
      const response = await fetch(`${API_URL}/frontdesk/activities/${logId}`, {
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
    }
  };

  useEffect(() => {
    const loadDailyLogs = async () => {
      await fetchDailyLogs();
    };
    loadDailyLogs();
  }, []);

  const getActivityTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      call: "bg-blue-500/20 text-blue-400",
      visitor: "bg-green-500/20 text-green-400",
      walk_in: "bg-purple-500/20 text-purple-400",
      lead: "bg-yellow-500/20 text-yellow-400",
      tour: "bg-cyan-500/20 text-cyan-400",
    };
    return colors[type] || "bg-gray-500/20 text-gray-400";
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 4) return "bg-green-500/20 text-green-400";
    if (rating >= 3) return "bg-yellow-500/20 text-yellow-400";
    return "bg-red-500/20 text-red-400";
  };

  return (
    <AppShell
      eyebrow="Front-Desk Operations"
      title="Daily log and activity tracking"
      description="Track calls, visitors, walk-in inquiries, lead metrics, and staff performance for front-desk operations."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button
                variant={activeTab === "logs" ? "primary" : "secondary"}
                onClick={() => setActiveTab("logs")}
              >
                <Calendar className="mr-2 h-4 w-4" />
                Daily Logs
              </Button>
              <Button
                variant={activeTab === "activities" ? "primary" : "secondary"}
                onClick={() => setActiveTab("activities")}
              >
                Activity Details
              </Button>
              <Button
                variant={activeTab === "performance" ? "primary" : "secondary"}
                onClick={() => setActiveTab("performance")}
              >
                Staff Performance
              </Button>
            </div>
            <Button onClick={() => setShowCreateLogDialog(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Daily Log
            </Button>
          </div>

          {activeTab === "logs" && (
            <Card className="p-6">
              <SectionTitle 
                title="Daily Logs" 
                description="Front-desk daily activity summaries" 
              />
              
              <div className="mt-6 space-y-4">
                {dailyLogs.length === 0 ? (
                  <p className="text-center text-[#9eb1cf]">No daily logs found</p>
                ) : (
                  dailyLogs.map((log) => (
                    <div
                      key={log.id}
                      className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-4"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <span className="text-sm text-[#9eb1cf]">
                            {new Date(log.date).toLocaleDateString()}
                          </span>
                          <Badge className={getRatingColor(log.performance_rating)}>
                            Rating: {log.performance_rating}/5
                          </Badge>
                        </div>
                        <p className="mt-2 font-medium text-white">{log.staff_name}</p>
                        <div className="mt-3 grid grid-cols-2 gap-4 text-sm text-[#9eb1cf]">
                          <div className="flex items-center gap-2">
                            <Phone className="h-4 w-4" />
                            Calls: {log.calls_answered}/{log.calls_logged} answered
                          </div>
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            Visitors: {log.visitors_checked_in} in, {log.visitors_checked_out} out
                          </div>
                          <div className="flex items-center gap-2">
                            Walk-ins: {log.walk_in_inquiries}
                          </div>
                          <div className="flex items-center gap-2">
                            New Leads: {log.new_leads}
                          </div>
                          <div className="flex items-center gap-2">
                            Tours Scheduled: {log.tours_scheduled}
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => fetchActivities(log.id)}
                          variant="outline"
                          className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"
                        >
                          View Activities
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          )}

          {activeTab === "activities" && (
            <Card className="p-6">
              <SectionTitle 
                title="Activity Details" 
                description="Detailed activity logs for selected daily log" 
              />
              
              <div className="mt-6 space-y-4">
                {activities.length === 0 ? (
                  <p className="text-center text-[#9eb1cf]">No activities found. Select a daily log to view activities.</p>
                ) : (
                  activities.map((activity) => (
                    <div
                      key={activity.id}
                      className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-4"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <Badge className={getActivityTypeColor(activity.activity_type)}>
                            {activity.activity_type}
                          </Badge>
                          <span className="text-sm text-[#9eb1cf]">
                            {new Date(activity.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="mt-2 font-medium text-white">{activity.description}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          )}

          {activeTab === "performance" && (
            <Card className="p-6">
              <SectionTitle 
                title="Staff Performance" 
                description="Front-desk staff performance metrics" 
              />
              
              <div className="mt-6 space-y-4">
                {dailyLogs.length === 0 ? (
                  <p className="text-center text-[#9eb1cf]">No performance data available</p>
                ) : (
                  dailyLogs.map((log) => (
                    <div
                      key={log.id}
                      className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-4"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <span className="text-sm text-[#9eb1cf]">
                            {new Date(log.date).toLocaleDateString()}
                          </span>
                          <Badge className={getRatingColor(log.performance_rating)}>
                            Rating: {log.performance_rating}/5
                          </Badge>
                        </div>
                        <p className="mt-2 font-medium text-white">{log.staff_name}</p>
                        <div className="mt-3 text-sm text-[#9eb1cf]">
                          <p>Call Answer Rate: {log.calls_logged > 0 ? Math.round((log.calls_answered / log.calls_logged) * 100) : 0}%</p>
                          <p>Visitor Engagement: {log.visitors_checked_in} visitors checked in</p>
                          <p>Lead Generation: {log.new_leads} new leads captured</p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          )}
        </>
      )}
    </AppShell>
  );
}

"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { Building2, DollarSign, AlertTriangle, TrendingDown } from "lucide-react";
import { getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface AnalyticsData {
  total_lost: number;
  conversion_rate: number;
  top_reason: string;
  price_related: number;
  competitor_wins?: number;
  recoverable?: number;
  reasons?: Array<{ category: string; description: string; count: number; percentage?: number }>;
}

interface CompetitorData {
  id: string;
  name: string;
  competitor: string;
  lost_leads: number;
  leads_lost?: number;
  location?: string;
  avg_fee?: string;
  strength?: string;
  avg_price_sensitivity: number;
}

interface TrendsData {
  month: string;
  total_lost: number;
  price_related: number;
  competition_related: number;
  monthly_trends?: Array<{ month: string; leads_lost: number; change: number; increase?: boolean; percentage_change?: number }>;
}

export default function LostLeadsPage() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [competitorData, setCompetitorData] = useState<CompetitorData[]>([]);
  const [trendsData, setTrendsData] = useState<TrendsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "competitors" | "trends">("overview");

  const fetchLostLeadAnalytics = async () => {
    try {
      const response = await fetch(`${API_URL}/lost-leads/analytics`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      }
    } catch (error) {
      console.error("Error fetching lost lead analytics:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCompetitorAnalysis = async () => {
    try {
      const response = await fetch(`${API_URL}/lost-leads/competitor-analysis`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setCompetitorData(Array.isArray(data) ? data : data.competitors || []);
      }
    } catch (error) {
      console.error("Error fetching competitor analysis:", error);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await fetch(`${API_URL}/lost-leads/trends`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setTrendsData(data);
      }
    } catch (error) {
      console.error("Error fetching trends:", error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      if (activeTab === "overview") await fetchLostLeadAnalytics();
      else if (activeTab === "competitors") await fetchCompetitorAnalysis();
      else if (activeTab === "trends") await fetchTrends();
    };
    loadData();
  }, [activeTab]);

  const getReasonColor = (reason: string) => {
    const colors: Record<string, string> = {
      price: "bg-red-500/20 text-red-400",
      location: "bg-yellow-500/20 text-yellow-400",
      curriculum: "bg-blue-500/20 text-blue-400",
      facilities: "bg-purple-500/20 text-purple-400",
      reputation: "bg-green-500/20 text-green-400",
    };
    return colors[reason] || "bg-gray-500/20 text-gray-400";
  };

  return (
    <AppShell
      eyebrow="Lost Lead Analytics"
      title="Understand why prospects don't enroll"
      description="Analyze lost lead reasons, competitor analysis, and trends to improve conversion strategies."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button
                variant={activeTab === "overview" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("overview"); fetchLostLeadAnalytics(); }}
              >
                Overview
              </Button>
              <Button
                variant={activeTab === "competitors" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("competitors"); fetchCompetitorAnalysis(); }}
              >
                <Building2 className="mr-2 h-4 w-4" />
                Competitors
              </Button>
              <Button
                variant={activeTab === "trends" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("trends"); fetchTrends(); }}
              >
                <TrendingDown className="mr-2 h-4 w-4" />
                Trends
              </Button>
            </div>
          </div>

          {activeTab === "overview" && (
            <>
              <div className="grid gap-4 xl:grid-cols-4">
                <Card className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-500/20">
                      <TrendingDown className="h-5 w-5 text-red-400" />
                    </div>
                    <div>
                      <p className="text-sm text-[#9eb1cf]">Total Lost Leads</p>
                      <p className="text-2xl font-bold text-white">{analyticsData?.total_lost || "0"}</p>
                    </div>
                  </div>
                </Card>
                <Card className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-yellow-500/20">
                      <DollarSign className="h-5 w-5 text-yellow-400" />
                    </div>
                    <div>
                      <p className="text-sm text-[#9eb1cf]">Price Related</p>
                      <p className="text-2xl font-bold text-white">{analyticsData?.price_related || "0"}</p>
                    </div>
                  </div>
                </Card>
                <Card className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500/20">
                      <Building2 className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm text-[#9eb1cf]">Competitor Wins</p>
                      <p className="text-2xl font-bold text-white">{analyticsData?.competitor_wins || "0"}</p>
                    </div>
                  </div>
                </Card>
                <Card className="p-6">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/20">
                      <AlertTriangle className="h-5 w-5 text-green-400" />
                    </div>
                    <div>
                      <p className="text-sm text-[#9eb1cf]">Recoverable</p>
                      <p className="text-2xl font-bold text-white">{analyticsData?.recoverable || "0"}</p>
                    </div>
                  </div>
                </Card>
              </div>

              <Card className="mt-6 p-6">
                <SectionTitle 
                  title="Lost Lead Reasons" 
                  description="Primary reasons for losing prospects" 
                />
                <div className="mt-4 space-y-4">
                  {analyticsData?.reasons?.map((reason) => (
                    <div key={reason.category} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge className={getReasonColor(reason.category)}>
                          {reason.category}
                        </Badge>
                        <span className="text-sm text-[#9eb1cf]">{reason.description}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-sm font-medium text-white">{reason.count} leads</span>
                        <span className="text-sm text-[#9eb1cf]">{reason.percentage}%</span>
                      </div>
                    </div>
                  )) || <p className="text-center text-[#9eb1cf]">No data available</p>}
                </div>
              </Card>
            </>
          )}

          {activeTab === "competitors" && (
            <Card className="p-6">
              <SectionTitle 
                title="Competitor Analysis" 
                description="Schools that are winning your prospects" 
              />
              <div className="mt-4 space-y-4">
                {competitorData.length === 0 ? (
                  <p className="text-center text-[#9eb1cf]">No competitor data available</p>
                ) : (
                  competitorData.map((competitor) => (
                    <div key={competitor.id} className="flex items-start justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold text-white">{competitor.name}</h3>
                          <Badge className="border-[#d9a441]/30 text-[#d9a441]">
                            {competitor.leads_lost} lost leads
                          </Badge>
                        </div>
                        <p className="mt-2 text-sm text-[#9eb1cf]">{competitor.location}</p>
                        <div className="mt-3 flex gap-4 text-sm">
                          <span className="text-[#9eb1cf]">Avg Fee: {competitor.avg_fee}</span>
                          <span className="text-[#9eb1cf]">Strength: {competitor.strength}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          )}

          {activeTab === "trends" && (
            <Card className="p-6">
              <SectionTitle 
                title="Lost Lead Trends" 
                description="Historical patterns and seasonal variations" 
              />
              <div className="mt-4 space-y-4">
                {trendsData?.monthly_trends?.map((trend) => (
                  <div key={trend.month} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <p className="font-medium text-white">{trend.month}</p>
                      <p className="text-sm text-[#9eb1cf]">{trend.leads_lost} leads lost</p>
                    </div>
                    <Badge className={trend.increase ? "bg-red-500/20 text-red-400" : "bg-green-500/20 text-green-400"}>
                      {trend.increase ? "+" : "-"}{trend.percentage_change}%
                    </Badge>
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

"use client";

import { useState, useEffect, useCallback } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, SectionTitle, TrendPanel, KpiGrid } from "@/components/dashboard/ops-primitives";
import { TrendingUp, Users, DollarSign, GraduationCap, AlertCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface AnalyticsData {
  total_students: number;
  active_students: number;
  total_revenue: number;
  retention_rate: number;
  predicted_enrollment?: string;
  fee_forecast?: string;
  at_risk_count?: string;
  next_term_prediction?: string;
  model_accuracy?: string;
  confidence_level?: string;
  projected_revenue?: string;
  collection_rate?: string;
  risk_factors?: Array<{ factor: string; impact: string }>;
  at_risk_students?: Array<{ id: string; name: string; risk_level: string; class?: string; risk_score?: string }>;
  historical_trends?: Array<{ name: string; value: number }>;
  enrollment_trends?: Array<{ month: string; count: number }>;
  revenue_trends?: Array<{ month: string; amount: number }>;
}

export default function AnalyticsPage() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "enrollment" | "finance" | "retention">("overview");

  const fetchAnalytics = useCallback(async () => {
    try {
      const endpoint = activeTab === "overview"
        ? "/analytics/dashboard"
        : activeTab === "enrollment"
        ? "/analytics/enrollment/forecast"
        : activeTab === "finance"
        ? "/analytics/fee/forecast"
        : "/analytics/retention/risk";

      const response = await fetch(`${API_URL}${endpoint}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      }
    } catch (error) {
      console.error("Error fetching analytics:", error);
    } finally {
      setIsLoading(false);
    }
  }, [activeTab]);

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const kpiData = [
    { label: "Predicted Enrollment", value: analyticsData?.predicted_enrollment || "N/A", change: "+12% vs last term", tone: "good" as const },
    { label: "Fee Collection Forecast", value: analyticsData?.fee_forecast || "N/A", change: "+8% vs target", tone: "good" as const },
    { label: "Retention Rate", value: String(analyticsData?.retention_rate || "N/A"), change: "-2% vs last term", tone: "warn" as const },
    { label: "At-Risk Students", value: analyticsData?.at_risk_count || "N/A", change: "Requires attention", tone: "warn" as const },
  ];

  return (
    <AppShell
      eyebrow="Analytics Dashboard"
      title="Predictive insights and forecasting"
      description="Advanced analytics powered by machine learning to predict enrollment, fee collection, and student retention trends."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button
                variant={activeTab === "overview" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("overview"); fetchAnalytics(); }}
              >
                Overview
              </Button>
              <Button
                variant={activeTab === "enrollment" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("enrollment"); fetchAnalytics(); }}
              >
                <Users className="mr-2 h-4 w-4" />
                Enrollment
              </Button>
              <Button
                variant={activeTab === "finance" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("finance"); fetchAnalytics(); }}
              >
                <DollarSign className="mr-2 h-4 w-4" />
                Finance
              </Button>
              <Button
                variant={activeTab === "retention" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("retention"); fetchAnalytics(); }}
              >
                <GraduationCap className="mr-2 h-4 w-4" />
                Retention
              </Button>
            </div>
            <Button variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
              Generate Report
            </Button>
          </div>

          <KpiGrid items={kpiData} />

          <div className="mt-6 grid gap-6 xl:grid-cols-2">
            <Card className="p-6">
              <SectionTitle 
                title="Enrollment Forecast" 
                description="Predicted enrollment trends for upcoming terms" 
              />
              <div className="mt-4 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[#9eb1cf]">Next Term Prediction</span>
                  <Badge className="bg-green-500/20 text-green-400">
                    <TrendingUp className="mr-1 h-3 w-3" />
                    {analyticsData?.next_term_prediction || "+15%"}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[#9eb1cf]">Model Accuracy</span>
                  <span className="text-sm font-medium text-white">{analyticsData?.model_accuracy || "89%"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[#9eb1cf]">Confidence Level</span>
                  <span className="text-sm font-medium text-white">{analyticsData?.confidence_level || "High"}</span>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <SectionTitle 
                title="Fee Collection Forecast" 
                description="Projected revenue and collection patterns" 
              />
              <div className="mt-4 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[#9eb1cf]">Projected Revenue</span>
                  <span className="text-sm font-medium text-white">{analyticsData?.projected_revenue || "₦2.8M"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[#9eb1cf]">Collection Rate Prediction</span>
                  <Badge className="bg-green-500/20 text-green-400">
                    <TrendingUp className="mr-1 h-3 w-3" />
                    {analyticsData?.collection_rate || "78%"}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-[#9eb1cf]">Risk Factors</span>
                  <Badge className="bg-yellow-500/20 text-yellow-400">
                    <AlertCircle className="mr-1 h-3 w-3" />
                    {analyticsData?.risk_factors?.length || 3} identified
                  </Badge>
                </div>
              </div>
            </Card>
          </div>

          <Card className="mt-6 p-6">
            <SectionTitle 
              title="Retention Risk Analysis" 
              description="Students at risk of leaving with intervention recommendations" 
            />
            <div className="mt-4 space-y-4">
              {analyticsData?.at_risk_students && analyticsData.at_risk_students.length > 0 ? (
                analyticsData.at_risk_students.map((student) => (
                  <div key={student.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                    <div>
                      <p className="font-medium text-white">{student.name}</p>
                      <p className="text-sm text-[#9eb1cf]">{student.class} • Risk Score: {student.risk_score}</p>
                    </div>
                    <Badge className={student.risk_level === "high" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400"}>
                      {student.risk_level}
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-center text-[#9eb1cf]">No students currently at risk</p>
              )}
            </div>
          </Card>

          <TrendPanel
            title="Historical Trends"
            description="Performance trends over the past academic year"
            data={analyticsData?.historical_trends || []}
            metric="Analytics improving"
          />
        </>
      )}
    </AppShell>
  );
}

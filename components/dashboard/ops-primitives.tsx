"use client";

import type { ReactNode } from "react";
import { ArrowRight, TrendingUp } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { ActivityItem, KpiCard, ReportPoint } from "@/types/crm";

export function LoadingPanel() {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, index) => (
        <Card key={index} className="animate-pulse bg-white/6 py-10" />
      ))}
    </div>
  );
}

export function SectionTitle({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <h2 className="font-serif text-2xl text-white">{title}</h2>
        <p className="mt-2 text-sm leading-6 text-[#9eb1cf]">{description}</p>
      </div>
      {action}
    </div>
  );
}

export function KpiGrid({ items }: { items: KpiCard[] }) {
  return (
    <div className="grid gap-4 xl:grid-cols-4 md:grid-cols-2">
      {items.map((item) => (
        <Card key={item.label} className="bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03))]">
          <p className="text-xs uppercase tracking-[0.3em] text-[#9eb1cf]">{item.label}</p>
          <div className="mt-4 flex items-end justify-between">
            <p className="font-serif text-4xl text-white">{item.value}</p>
            <Badge tone={item.tone}>{item.change}</Badge>
          </div>
        </Card>
      ))}
    </div>
  );
}

export function InsightFeed({ items }: { items: ActivityItem[] }) {
  return (
    <Card className="space-y-4">
      <SectionTitle title="Operational Feed" description="Live movement across finance, admissions, support, and classroom operations." />
      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.title} className="rounded-3xl border border-white/10 bg-white/5 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-white">{item.title}</p>
                <p className="mt-1 text-sm text-[#9eb1cf]">{item.subtitle}</p>
              </div>
              <Badge tone={item.tone}>{item.time}</Badge>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

export function TrendPanel({
  title,
  description,
  data,
  metric,
}: {
  title: string;
  description: string;
  data: ReportPoint[];
  metric: string;
}) {
  return (
    <Card className="space-y-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-white">{title}</p>
          <p className="mt-1 text-sm text-[#9eb1cf]">{description}</p>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-medium text-emerald-200">
          <TrendingUp className="h-3.5 w-3.5" />
          {metric}
        </div>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="goldArea" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#d9a441" stopOpacity={0.65} />
                <stop offset="100%" stopColor="#d9a441" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
            <XAxis axisLine={false} tickLine={false} dataKey="name" tick={{ fill: "#9eb1cf", fontSize: 12 }} />
            <Tooltip
              cursor={{ stroke: "rgba(217,164,65,0.4)" }}
              contentStyle={{
                backgroundColor: "#0f172a",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 16,
                color: "#f6f1e8",
              }}
            />
            <Area type="monotone" dataKey="value" stroke="#d9a441" fill="url(#goldArea)" strokeWidth={3} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export function DataTable({
  title,
  description,
  columns,
  rows,
}: {
  title: string;
  description: string;
  columns: string[];
  rows: Array<Array<string | ReactNode>>;
}) {
  return (
    <Card className="overflow-hidden p-0">
      <div className="border-b border-white/10 px-6 py-5">
        <SectionTitle title={title} description={description} />
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left">
          <thead className="bg-white/5 text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-6 py-4 font-medium">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index} className="border-t border-white/6 text-sm text-[#d6dfef]">
                {row.map((cell, cellIndex) => (
                  <td key={`${index}-${cellIndex}`} className="px-6 py-4 align-top">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

export function ActionHint({ text }: { text: string }) {
  return (
    <div className="inline-flex items-center gap-2 text-sm text-[#d9a441]">
      <span>{text}</span>
      <ArrowRight className="h-4 w-4" />
    </div>
  );
}

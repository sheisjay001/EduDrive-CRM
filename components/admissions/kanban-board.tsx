"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { MoreVertical } from "lucide-react";
import type { LeadItem, StageCard } from "@/types/crm";

const STAGES = [
  "new",
  "contacted",
  "tour_scheduled",
  "assessment_booked",
  "offered",
  "enrolled",
  "lost",
];

interface KanbanBoardProps {
  leads: LeadItem[];
  pipeline: StageCard[];
  onStageChange?: (leadId: string, newStage: string) => void;
}

export function KanbanBoard({ leads, pipeline, onStageChange }: KanbanBoardProps) {
  const [draggedLead, setDraggedLead] = useState<string | null>(null);

  const getLeadsByStage = (stage: string) => {
    return leads.filter((lead) => lead.stage === stage);
  };

  const getStageLabel = (stage: string) => {
    const stageMap: Record<string, string> = {
      new: "New Leads",
      contacted: "Contacted",
      tour_scheduled: "Tour Scheduled",
      assessment_booked: "Assessment Booked",
      offered: "Offered",
      enrolled: "Enrolled",
      lost: "Lost",
    };
    return stageMap[stage] || stage;
  };

  const getStageCount = (stage: string) => {
    return pipeline.find((p) => p.stage === stage)?.count || 0;
  };

  const handleDragStart = (leadId: string) => {
    setDraggedLead(leadId);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (targetStage: string) => {
    if (draggedLead && onStageChange) {
      onStageChange(draggedLead, targetStage);
    }
    setDraggedLead(null);
  };

  return (
    <div className="grid gap-4 xl:grid-cols-4 lg:grid-cols-3 md:grid-cols-2">
      {STAGES.map((stage) => {
        const stageLeads = getLeadsByStage(stage);
        const count = getStageCount(stage);

        return (
          <motion.div
            key={stage}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col gap-3"
          >
            <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
              <p className="text-sm font-semibold text-white">{getStageLabel(stage)}</p>
              <Badge tone="warn">{count}</Badge>
            </div>

            <div
              className="flex min-h-[200px] flex-col gap-3 rounded-2xl border border-dashed border-white/10 bg-white/[0.02] p-3"
              onDragOver={handleDragOver}
              onDrop={() => handleDrop(stage)}
            >
              {stageLeads.map((lead) => (
                <motion.div
                  key={lead.id}
                  draggable
                  onDragStart={() => handleDragStart(lead.id)}
                  whileDrag={{ scale: 1.02, boxShadow: "0 8px 30px rgba(217,164,65,0.2)" }}
                  className="cursor-grab rounded-2xl border border-white/10 bg-white/5 p-4 transition hover:border-white/20 hover:bg-white/8 active:cursor-grabbing"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-white">{lead.childName}</p>
                      <p className="mt-1 text-xs text-[#9eb1cf]">{lead.parentName}</p>
                    </div>
                    <button className="text-[#9eb1cf] transition hover:text-white">
                      <MoreVertical className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="mt-3 flex items-center gap-2">
                    <Badge tone="neutral" className="text-xs">
                      {lead.source}
                    </Badge>
                    {lead.classInterest && (
                      <span className="text-xs text-[#9eb1cf]">{lead.classInterest}</span>
                    )}
                  </div>
                </motion.div>
              ))}

              {stageLeads.length === 0 && (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <p className="text-sm text-[#9eb1cf]">No leads in this stage</p>
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

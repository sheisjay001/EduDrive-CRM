"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { KanbanBoard } from "@/components/admissions/kanban-board";
import { CreateLeadDialog } from "@/components/admissions/create-lead-dialog";
import { useAdmissionsQuery } from "@/hooks/use-crm-query";
import { apiClient } from "@/services/api-client";
import { Plus } from "lucide-react";

export default function AdmissionsPage() {
  const { data, isLoading } = useAdmissionsQuery();
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [viewMode, setViewMode] = useState<"kanban" | "list">("kanban");

  const handleCreateLead = async (leadData: any) => {
    try {
      await apiClient.createLead(leadData);
      // Refresh data after creation
      window.location.reload();
    } catch (error) {
      console.error("Failed to create lead:", error);
    }
  };

  const handleStageChange = async (leadId: string, newStage: string) => {
    try {
      await apiClient.updateLeadStage(leadId, newStage);
      // Refresh data after update
      window.location.reload();
    } catch (error) {
      console.error("Failed to update lead stage:", error);
    }
  };

  return (
    <AppShell
      eyebrow="Admissions Workspace"
      title="Keep every lead moving"
      description="Manage inquiry sources, stage visibility, assessment planning, and fast follow-up without losing context between admissions officers."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button
                variant={viewMode === "kanban" ? "primary" : "secondary"}
                onClick={() => setViewMode("kanban")}
              >
                Kanban Board
              </Button>
              <Button
                variant={viewMode === "list" ? "primary" : "secondary"}
                onClick={() => setViewMode("list")}
              >
                List View
              </Button>
            </div>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="mr-2 h-4 w-4" />
              New Lead
            </Button>
          </div>

          {viewMode === "kanban" ? (
            <Card className="p-6">
              <SectionTitle title="Pipeline board" description="Drag leads between stages to update their status." />
              <KanbanBoard
                leads={data.leads}
                pipeline={data.pipeline}
                onStageChange={handleStageChange}
              />
            </Card>
          ) : (
            <DataTable
              title="Priority lead queue"
              description="The leads most likely to move when the team follows up today."
              columns={["Lead ID", "Child", "Parent", "Source", "Stage", "Class", "Follow-up"]}
              rows={data.leads.map((lead) => [
                <Link key={lead.id} href={`/admissions/${lead.id}`} className="font-medium text-[#d9a441] hover:underline">
                  {lead.id}
                </Link>,
                lead.childName,
                lead.parentName,
                lead.source,
                <Badge key={`${lead.id}-stage`} tone="neutral">{lead.stage}</Badge>,
                lead.classInterest,
                lead.followUp,
              ])}
            />
          )}

          <CreateLeadDialog
            open={showCreateDialog}
            onOpenChange={setShowCreateDialog}
            onSubmit={handleCreateLead}
          />
        </>
      )}
    </AppShell>
  );
}

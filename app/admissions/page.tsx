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
import { Plus, Edit, Trash2, Save, X } from "lucide-react";
import { getUser, getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function AdmissionsPage() {
  const { data, isLoading, refetch } = useAdmissionsQuery();
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [viewMode, setViewMode] = useState<"kanban" | "list">("kanban");
  const [editingLead, setEditingLead] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState({});

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "admissions_officer"].includes(userRole);
  const canDelete = userRole === "school_admin";

  const handleCreateLead = async (leadData: Record<string, unknown>) => {
    try {
      await apiClient.createLead(leadData);
      setShowCreateDialog(false);
      refetch();
    } catch (error) {
      console.error("Failed to create lead:", error);
    }
  };

  const handleStageChange = async (leadId: string, newStage: string) => {
    try {
      await apiClient.updateLeadStage(leadId, newStage);
      refetch();
    } catch (error) {
      console.error("Failed to update lead stage:", error);
    }
  };

  const handleEdit = (lead: { id: string; childName: string; parentName: string; source: string; stage: string; classInterest: string; followUp: string }) => {
    setEditingLead(lead.id);
    setEditFormData({
      first_name: lead.childName?.split(" ")[0],
      last_name: lead.childName?.split(" ")[1] || "",
      parent_name: lead.parentName,
      source: lead.source,
      stage: lead.stage,
      interested_class: lead.classInterest,
    });
  };

  const handleSaveEdit = async (leadId: string) => {
    try {
      const response = await fetch(`${API_URL}/leads/${leadId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getAccessToken()}`,
        },
        body: JSON.stringify(editFormData),
      });

      if (response.ok) {
        setEditingLead(null);
        refetch();
        alert("Lead updated successfully");
      } else {
        alert("Failed to update lead");
      }
    } catch (error) {
      alert("Error updating lead");
    }
  };

  const handleCancelEdit = () => {
    setEditingLead(null);
    setEditFormData({});
  };

  const handleDelete = async (leadId: string) => {
    if (!confirm("Are you sure you want to delete this lead?")) return;

    try {
      const response = await fetch(`${API_URL}/leads/${leadId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });

      if (response.ok) {
        refetch();
        alert("Lead deleted successfully");
      } else {
        alert("Failed to delete lead");
      }
    } catch (error) {
      alert("Error deleting lead");
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
            <div className="flex gap-2">
              <Button asChild variant="secondary">
                <Link href="/admissions/calendar">Schedule Center</Link>
              </Button>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                New Lead
              </Button>
            </div>
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
              columns={["Lead ID", "Child", "Parent", "Source", "Stage", "Class", "Follow-up", "Actions"]}
              rows={data.leads.map((lead: any) => [ // eslint-disable-line @typescript-eslint/no-explicit-any
                <Link key={lead.id} href={`/admissions/${lead.id}`} className="font-medium text-[#d9a441] hover:underline">
                  {lead.id}
                </Link>,
                editingLead === lead.id ? (
                  <input
                    key="child_name"
                    type="text"
                    defaultValue={lead.childName}
                    onChange={(e) => setEditFormData({ ...editFormData, first_name: e.target.value.split(" ")[0], last_name: e.target.value.split(" ")[1] || "" })}
                    className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
                  />
                ) : (
                  lead.childName
                ),
                lead.parentName,
                lead.source,
                <Badge key={`${lead.id}-stage`} tone="neutral">{lead.stage}</Badge>,
                lead.classInterest,
                lead.followUp,
                <div key={`${lead.id}-actions`} className="flex gap-2">
                  {editingLead === lead.id ? (
                    <>
                      <Button size="sm" onClick={() => handleSaveEdit(lead.id)} className="bg-green-600 text-white hover:bg-green-700">
                        <Save className="h-4 w-4" />
                      </Button>
                      <Button size="sm" onClick={handleCancelEdit} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                        <X className="h-4 w-4" />
                      </Button>
                    </>
                  ) : (
                    <>
                      {canEdit && (
                        <Button size="sm" onClick={() => handleEdit(lead)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                          <Edit className="h-4 w-4" />
                        </Button>
                      )}
                      {canDelete && (
                        <Button size="sm" onClick={() => handleDelete(lead.id)} variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </>
                  )}
                </div>,
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

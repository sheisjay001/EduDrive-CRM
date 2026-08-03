"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useHelpdeskQuery } from "@/hooks/use-crm-query";
import { Edit, Trash2, Save, X, Plus } from "lucide-react";
import { getUser } from "@/services/auth-storage";
import { apiClient } from "@/services/api-client";

export default function HelpdeskPage() {
  const { data, isLoading, refetch } = useHelpdeskQuery();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTicket, setEditingTicket] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState({});
  const [addFormData, setAddFormData] = useState({ subject: "", parent_id: "", priority: "", assignee_id: "" });

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "helpdesk_officer"].includes(userRole);
  const canDelete = userRole === "school_admin";

  const handleEdit = (ticket: { id: string; subject: string; parent: string; priority: string; assignee: string; sla: string; status: string }) => {
    setEditingTicket(ticket.id);
    setEditFormData({ subject: ticket.subject, priority: ticket.priority, status: ticket.status });
  };

  const handleSaveEdit = async (ticketId: string) => {
    try {
      await apiClient.updateTicket(ticketId, editFormData);
      setEditingTicket(null);
      refetch();
      alert("Ticket updated");
    } catch { alert("Error updating ticket"); }
  };

  const handleCancelEdit = () => { setEditingTicket(null); setEditFormData({}); };

  const handleDelete = async (ticketId: string) => {
    if (!confirm("Delete this ticket?")) return;
    try {
      await apiClient.deleteTicket(ticketId);
      refetch();
      alert("Ticket deleted");
    } catch { alert("Error deleting ticket"); }
  };

  const handleAdd = async () => {
    try {
      await apiClient.createTicket(addFormData);
      setShowAddForm(false);
      setAddFormData({ subject: "", parent_id: "", priority: "", assignee_id: "" });
      refetch();
      alert("Ticket created");
    } catch { alert("Error creating ticket"); }
  };

  return (
    <AppShell
      eyebrow="Help Desk"
      title="Keep complaints moving toward resolution"
      description="Track SLA pressure, assign the right internal owner, and give school leadership visibility into recurring parent pain points."
    >
      {canEdit && (
        <div className="mb-6">
          {!showAddForm ? (
            <Button onClick={() => setShowAddForm(true)} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
              <Plus className="h-4 w-4 mr-2" /> Add Ticket
            </Button>
          ) : (
            <div className="flex gap-2 items-center flex-wrap">
              <input type="text" placeholder="Subject" value={addFormData.subject} onChange={(e) => setAddFormData({ ...addFormData, subject: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Parent ID" value={addFormData.parent_id} onChange={(e) => setAddFormData({ ...addFormData, parent_id: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Priority" value={addFormData.priority} onChange={(e) => setAddFormData({ ...addFormData, priority: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Assignee ID" value={addFormData.assignee_id} onChange={(e) => setAddFormData({ ...addFormData, assignee_id: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <Button onClick={handleAdd} className="bg-green-600 text-white hover:bg-green-700">Save</Button>
              <Button onClick={() => setShowAddForm(false)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">Cancel</Button>
            </div>
          )}
        </div>
      )}
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <DataTable
          title="Active complaint board"
          description="A practical queue for parent support, bursary issues, and school operations complaints."
          columns={["Ticket", "Subject", "Parent", "Priority", "Assignee", "SLA", "Status", "Actions"]}
          rows={data.tickets.map((ticket) => [
            <Link key={`${ticket.id}-link`} href={`/helpdesk/${ticket.id}`} className="font-medium text-[#d9a441] hover:underline">
              {ticket.id}
            </Link>,
            editingTicket === ticket.id ? (
              <input type="text" defaultValue={ticket.subject} onChange={(e) => setEditFormData({ ...editFormData, subject: e.target.value })} className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white" />
            ) : (
              ticket.subject
            ),
            ticket.parent,
            editingTicket === ticket.id ? (
              <input type="text" defaultValue={ticket.priority} onChange={(e) => setEditFormData({ ...editFormData, priority: e.target.value })} className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white" />
            ) : (
              <Badge key={`${ticket.id}-priority`} tone={ticket.priority === "Urgent" ? "danger" : ticket.priority === "High" ? "warn" : "neutral"}>
                {ticket.priority}
              </Badge>
            ),
            ticket.assignee,
            ticket.sla,
            editingTicket === ticket.id ? (
              <input type="text" defaultValue={ticket.status} onChange={(e) => setEditFormData({ ...editFormData, status: e.target.value })} className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white" />
            ) : (
              <Badge key={`${ticket.id}-status`} tone={ticket.status === "Resolved" ? "good" : "warn"}>
                {ticket.status}
              </Badge>
            ),
            <div key={`${ticket.id}-actions`} className="flex gap-2">
              {editingTicket === ticket.id ? (
                <>
                  <Button size="sm" onClick={() => handleSaveEdit(ticket.id)} className="bg-green-600 text-white hover:bg-green-700"><Save className="h-4 w-4" /></Button>
                  <Button size="sm" onClick={handleCancelEdit} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><X className="h-4 w-4" /></Button>
                </>
              ) : (
                <>
                  {canEdit && <Button size="sm" onClick={() => handleEdit(ticket)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><Edit className="h-4 w-4" /></Button>}
                  {canDelete && <Button size="sm" onClick={() => handleDelete(ticket.id)} variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10"><Trash2 className="h-4 w-4" /></Button>}
                </>
              )}
            </div>,
          ])}
        />
      )}
    </AppShell>
  );
}

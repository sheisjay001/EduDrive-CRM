"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useMessageTemplatesQuery } from "@/hooks/use-crm-query";
import { Edit, Trash2, Save, X, Plus } from "lucide-react";
import { getUser } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function MessageTemplatesPage() {
  const { data, isLoading, refetch } = useMessageTemplatesQuery();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState({});
  const [addFormData, setAddFormData] = useState({ name: "", channel: "", use_case: "", content: "" });

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "admissions_officer"].includes(userRole);
  const canDelete = userRole === "school_admin";

  const handleEdit = (template: { id: string; name: string; channel: string; useCase: string; lastEdited: string; content?: string }) => {
    setEditingTemplate(template.id);
    setEditFormData({ name: template.name, channel: template.channel, use_case: template.useCase, content: template.content });
  };

  const handleSaveEdit = async (templateId: string) => {
    try {
      const response = await fetch(`${API_URL}/messaging/templates/${templateId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        body: JSON.stringify(editFormData),
      });
      if (response.ok) { setEditingTemplate(null); refetch(); alert("Template updated"); }
    } catch { alert("Error updating template"); }
  };

  const handleCancelEdit = () => { setEditingTemplate(null); setEditFormData({}); };

  const handleDelete = async (templateId: string) => {
    if (!confirm("Delete this template?")) return;
    try {
      const response = await fetch(`${API_URL}/messaging/templates/${templateId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
      });
      if (response.ok) { refetch(); alert("Template deleted"); }
    } catch { alert("Error deleting template"); }
  };

  const handleAdd = async () => {
    try {
      const response = await fetch(`${API_URL}/messaging/templates`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        body: JSON.stringify(addFormData),
      });
      if (response.ok) { setShowAddForm(false); setAddFormData({ name: "", channel: "", use_case: "", content: "" }); refetch(); alert("Template created"); }
    } catch { alert("Error creating template"); }
  };

  return (
    <AppShell
      eyebrow="Message templates"
      title="Reusable communication assets"
      description="Manage the reusable templates that power announcements, reminders, receipts, and support notifications."
    >
      {canEdit && (
        <div className="mb-6">
          {!showAddForm ? (
            <Button onClick={() => setShowAddForm(true)} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
              <Plus className="h-4 w-4 mr-2" /> Add Template
            </Button>
          ) : (
            <div className="flex gap-2 items-center flex-wrap">
              <input type="text" placeholder="Name" value={addFormData.name} onChange={(e) => setAddFormData({ ...addFormData, name: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Channel" value={addFormData.channel} onChange={(e) => setAddFormData({ ...addFormData, channel: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Use Case" value={addFormData.use_case} onChange={(e) => setAddFormData({ ...addFormData, use_case: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Content" value={addFormData.content} onChange={(e) => setAddFormData({ ...addFormData, content: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <Button onClick={handleAdd} className="bg-green-600 text-white hover:bg-green-700">Save</Button>
              <Button onClick={() => setShowAddForm(false)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">Cancel</Button>
            </div>
          )}
        </div>
      )}
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          {data.templates.map((template: { id: string; name: string; channel: string; useCase: string; lastEdited: string }) => (
            <Card key={template.id} className="space-y-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  {editingTemplate === template.id ? (
                    <input type="text" defaultValue={template.name} onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })} className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white" />
                  ) : (
                    <p className="text-sm text-[#9eb1cf]">{template.channel}</p>
                  )}
                  {editingTemplate === template.id ? (
                    <input type="text" defaultValue={template.name} onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })} className="mt-2 rounded border border-white/20 bg-white/10 px-2 py-1 text-2xl font-semibold text-white" />
                  ) : (
                    <p className="mt-2 text-2xl font-semibold text-white">{template.name}</p>
                  )}
                </div>
                <div className="flex gap-2 items-center">
                  {editingTemplate === template.id ? (
                    <>
                      <Button size="sm" onClick={() => handleSaveEdit(template.id)} className="bg-green-600 text-white hover:bg-green-700"><Save className="h-4 w-4" /></Button>
                      <Button size="sm" onClick={handleCancelEdit} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><X className="h-4 w-4" /></Button>
                    </>
                  ) : (
                    <>
                      {canEdit && <Button size="sm" onClick={() => handleEdit(template)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><Edit className="h-4 w-4" /></Button>}
                      {canDelete && <Button size="sm" onClick={() => handleDelete(template.id)} variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10"><Trash2 className="h-4 w-4" /></Button>}
                    </>
                  )}
                  <Badge tone="neutral">{template.useCase}</Badge>
                </div>
              </div>
              <p className="text-sm leading-7 text-[#d6dfef]">Last edited {template.lastEdited}.</p>
              <div className="text-sm text-[#9eb1cf]">
                <Link href="#" className="text-[#d9a441] underline">
                  Preview template
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}

"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useParentsQuery } from "@/hooks/use-crm-query";
import { Plus, Edit, Trash2, Save, X } from "lucide-react";
import { getUser } from "@/services/auth-storage";
import { apiClient } from "@/services/api-client";

export default function ParentsPage() {
  const { data, isLoading, refetch } = useParentsQuery();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingParent, setEditingParent] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState<{ full_name?: string; email?: string; phone?: string; relationship?: string }>({});
  const [addFormData, setAddFormData] = useState({ full_name: "", email: "", phone: "", relationship: "", family_id: "" });

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "admissions_officer"].includes(userRole);
  const canDelete = userRole === "school_admin";

  const handleEdit = (parent: { id: string; name: string; email: string; phone: string; relationship: string; studentName: string; status: string }) => {
    setEditingParent(parent.id);
    setEditFormData({
      full_name: parent.name,
      email: parent.email,
      phone: parent.phone,
      relationship: parent.relationship,
    });
  };

  const handleSaveEdit = async (parentId: string) => {
    try {
      await apiClient.updateParent(parentId, editFormData);
      setEditingParent(null);
      setEditFormData({});
      refetch();
      alert("Parent updated successfully");
    } catch (error) {
      alert("Error updating parent");
    }
  };

  const handleCancelEdit = () => {
    setEditingParent(null);
    setEditFormData({});
  };

  const handleDelete = async (parentId: string) => {
    if (!confirm("Are you sure you want to delete this parent?")) return;

    try {
      await apiClient.deleteParent(parentId);
      refetch();
      alert("Parent deleted successfully");
    } catch (error) {
      alert("Error deleting parent");
    }
  };

  const handleAdd = async () => {
    try {
      await apiClient.createParent(addFormData);
      setShowAddForm(false);
      setAddFormData({ full_name: "", email: "", phone: "", relationship: "", family_id: "" });
      refetch();
      alert("Parent created successfully");
    } catch (error) {
      alert("Error creating parent");
    }
  };

  return (
    <AppShell
      eyebrow="Parent Directory"
      title="Parent relationships"
      description="Manage guardian contacts, linked students, and channel preferences for parent communication."
    >
      {canEdit && (
        <div className="mb-6">
          {!showAddForm ? (
            <Button
              onClick={() => setShowAddForm(true)}
              className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Parent
            </Button>
          ) : (
            <div className="flex gap-2 items-center flex-wrap">
              <input
                type="text"
                placeholder="Full Name"
                value={addFormData.full_name}
                onChange={(e) => setAddFormData({ ...addFormData, full_name: e.target.value })}
                className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
              />
              <input
                type="email"
                placeholder="Email"
                value={addFormData.email}
                onChange={(e) => setAddFormData({ ...addFormData, email: e.target.value })}
                className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
              />
              <input
                type="text"
                placeholder="Phone"
                value={addFormData.phone}
                onChange={(e) => setAddFormData({ ...addFormData, phone: e.target.value })}
                className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
              />
              <input
                type="text"
                placeholder="Relationship"
                value={addFormData.relationship}
                onChange={(e) => setAddFormData({ ...addFormData, relationship: e.target.value })}
                className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
              />
              <input
                type="text"
                placeholder="Family ID"
                value={addFormData.family_id}
                onChange={(e) => setAddFormData({ ...addFormData, family_id: e.target.value })}
                className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
              />
              <Button onClick={handleAdd} className="bg-green-600 text-white hover:bg-green-700">
                Save
              </Button>
              <Button onClick={() => setShowAddForm(false)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                Cancel
              </Button>
            </div>
          )}
        </div>
      )}
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <DataTable
          title="Parent index"
          description="A unified list of active parent contacts linked to student records."
          columns={["Parent", "Relationship", "Student", "Phone", "Email", "Status", "Actions"]}
          rows={data.parents.map((parent) => [
            editingParent === parent.id ? (
              <input
                key="full_name"
                type="text"
                value={editFormData.full_name ?? ""}
                onChange={(e) => setEditFormData({ ...editFormData, full_name: e.target.value })}
                className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
              />
            ) : (
              <Link key={parent.id} href={`/parents/${parent.id}`} className="font-medium text-[#d9a441] hover:underline">
                {parent.name}
              </Link>
            ),
            parent.relationship,
            parent.studentName,
            parent.phone,
            parent.email,
            <Badge key={`${parent.id}-status`} tone={parent.status === "Active" ? "good" : "warn"}>
              {parent.status}
            </Badge>,
            <div key={`${parent.id}-actions`} className="flex gap-2">
              {editingParent === parent.id ? (
                <>
                  <Button size="sm" onClick={() => handleSaveEdit(parent.id)} className="bg-green-600 text-white hover:bg-green-700">
                    <Save className="h-4 w-4" />
                  </Button>
                  <Button size="sm" onClick={handleCancelEdit} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                    <X className="h-4 w-4" />
                  </Button>
                </>
              ) : (
                <>
                  {canEdit && (
                    <Button size="sm" onClick={() => handleEdit(parent)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                      <Edit className="h-4 w-4" />
                    </Button>
                  )}
                  {canDelete && (
                    <Button size="sm" onClick={() => handleDelete(parent.id)} variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </>
              )}
            </div>,
          ])}
        />
      )}
    </AppShell>
  );
}

"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useFamiliesQuery } from "@/hooks/use-crm-query";
import { Plus, Edit, Trash2, Save, X } from "lucide-react";
import { getUser, getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function FamiliesPage() {
  const { data, isLoading, refetch } = useFamiliesQuery();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingFamily, setEditingFamily] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState<{ household_name?: string; billing_contact_parent_id?: string }>({});
  const [addFormData, setAddFormData] = useState({ household_name: "", billing_contact_parent_id: "" });

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "admissions_officer"].includes(userRole);
  const canDelete = userRole === "school_admin";

  const handleEdit = (family: { id: string; household_name?: string; householdName?: string; billing_contact_parent_id?: string; billingContactParentId?: string }) => {
    setEditingFamily(family.id);
    setEditFormData({
      household_name: family.household_name || family.householdName || "",
      billing_contact_parent_id: family.billing_contact_parent_id || family.billingContactParentId || "",
    });
  };

  const handleSaveEdit = async (familyId: string) => {
    try {
      const response = await fetch(`${API_URL}/families/${familyId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getAccessToken()}`,
        },
        body: JSON.stringify(editFormData),
      });

      if (response.ok) {
        setEditingFamily(null);
        refetch();
        alert("Family updated successfully");
      } else {
        alert("Failed to update family");
      }
    } catch {
      alert("Error updating family");
    }
  };

  const handleCancelEdit = () => {
    setEditingFamily(null);
    setEditFormData({});
  };

  const handleDelete = async (familyId: string) => {
    if (!confirm("Are you sure you want to delete this family?")) return;

    try {
      const response = await fetch(`${API_URL}/families/${familyId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });

      if (response.ok) {
        refetch();
        alert("Family deleted successfully");
      } else {
        alert("Failed to delete family");
      }
    } catch {
      alert("Error deleting family");
    }
  };

  const handleAdd = async () => {
    try {
      const response = await fetch(`${API_URL}/families`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getAccessToken()}`,
        },
        body: JSON.stringify(addFormData),
      });

      if (response.ok) {
        setShowAddForm(false);
        setAddFormData({ household_name: "", billing_contact_parent_id: "" });
        refetch();
        alert("Family created successfully");
      } else {
        alert("Failed to create family");
      }
    } catch {
      alert("Error creating family");
    }
  };

  return (
    <AppShell
      eyebrow="Household Management"
      title="See the full family picture"
      description="Organize siblings, primary contacts, balance ownership, and parent-facing communication around households instead of isolated student records."
    >
      {canEdit && (
        <div className="mb-6">
          {!showAddForm ? (
            <Button
              onClick={() => setShowAddForm(true)}
              className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Family
            </Button>
          ) : (
            <div className="flex gap-2 items-center">
              <input
                type="text"
                placeholder="Household Name"
                value={addFormData.household_name}
                onChange={(e) => setAddFormData({ ...addFormData, household_name: e.target.value })}
                className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
              />
              <input
                type="text"
                placeholder="Billing Contact Parent ID"
                value={addFormData.billing_contact_parent_id}
                onChange={(e) => setAddFormData({ ...addFormData, billing_contact_parent_id: e.target.value })}
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
          title="Active households"
          description="A single view of who is responsible for communication, billing, and student support."
          columns={["Household", "Guardians", "Students", "Balance", "Status", "Actions"]}
          rows={data.households.map((family) => [
            editingFamily === family.id ? (
              <input
                key="household_name"
                type="text"
                value={editFormData.household_name ?? ""}
                onChange={(e) => setEditFormData({ ...editFormData, household_name: e.target.value })}
                className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white"
              />
            ) : (
              <Link key={family.id} href={`/families/${family.id}`} className="font-medium text-[#d9a441] hover:underline">
                {family.householdName}
              </Link>
            ),
            family.guardians.join(", "),
            `${family.students}`,
            family.balance,
            <Badge key={`${family.id}-status`} tone={family.status === "Up to date" ? "good" : "warn"}>
              {family.status}
            </Badge>,
            <div key={`${family.id}-actions`} className="flex gap-2">
              {editingFamily === family.id ? (
                <>
                  <Button size="sm" onClick={() => handleSaveEdit(family.id)} className="bg-green-600 text-white hover:bg-green-700">
                    <Save className="h-4 w-4" />
                  </Button>
                  <Button size="sm" onClick={handleCancelEdit} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                    <X className="h-4 w-4" />
                  </Button>
                </>
              ) : (
                <>
                  {canEdit && (
                    <Button size="sm" onClick={() => handleEdit(family)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                      <Edit className="h-4 w-4" />
                    </Button>
                  )}
                  {canDelete && (
                    <Button size="sm" onClick={() => handleDelete(family.id)} variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
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

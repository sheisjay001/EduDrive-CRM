"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useFeeStructuresQuery } from "@/hooks/use-crm-query";
import { Plus, Edit, Trash2, Save, X } from "lucide-react";
import { getUser, getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function FeeStructuresPage() {
  const { data, isLoading, refetch } = useFeeStructuresQuery();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingFee, setEditingFee] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState({});
  const [addFormData, setAddFormData] = useState({ class_id: "", term_name: "", title: "", amount: "", due_days: "" });

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "bursar"].includes(userRole);
  const canDelete = userRole === "school_admin";

  const handleEdit = (fee: { id: string; termName: string; title: string; amount: string; dueDays: number; className: string }) => {
    setEditingFee(fee.id);
    setEditFormData({ term_name: fee.termName, title: fee.title, amount: fee.amount, due_days: fee.dueDays });
  };

  const handleSaveEdit = async (feeId: string) => {
    try {
      const response = await fetch(`${API_URL}/finance/fee-structures/${feeId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${getAccessToken()}` },
        body: JSON.stringify(editFormData),
      });
      if (response.ok) { setEditingFee(null); refetch(); alert("Fee structure updated"); }
    } catch { alert("Error updating fee structure"); }
  };

  const handleCancelEdit = () => { setEditingFee(null); setEditFormData({}); };

  const handleDelete = async (feeId: string) => {
    if (!confirm("Delete this fee structure?")) return;
    try {
      const response = await fetch(`${API_URL}/finance/fee-structures/${feeId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${getAccessToken()}` },
      });
      if (response.ok) { refetch(); alert("Fee structure deleted"); }
    } catch { alert("Error deleting fee structure"); }
  };

  const handleAdd = async () => {
    try {
      const response = await fetch(`${API_URL}/finance/fee-structures`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${getAccessToken()}` },
        body: JSON.stringify(addFormData),
      });
      if (response.ok) { setShowAddForm(false); setAddFormData({ class_id: "", term_name: "", title: "", amount: "", due_days: "" }); refetch(); alert("Fee structure created"); }
    } catch { alert("Error creating fee structure"); }
  };

  return (
    <AppShell
      eyebrow="Fee structure manager"
      title="Term fees and billing rules"
      description="Define class-level fee bundles, due date rules, and optional charges for the current term."
    >
      {canEdit && (
        <div className="mb-6">
          {!showAddForm ? (
            <Button onClick={() => setShowAddForm(true)} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
              <Plus className="h-4 w-4 mr-2" /> Add Fee Structure
            </Button>
          ) : (
            <div className="flex gap-2 items-center flex-wrap">
              <input type="text" placeholder="Class ID" value={addFormData.class_id} onChange={(e) => setAddFormData({ ...addFormData, class_id: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Term Name" value={addFormData.term_name} onChange={(e) => setAddFormData({ ...addFormData, term_name: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Title" value={addFormData.title} onChange={(e) => setAddFormData({ ...addFormData, title: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Amount" value={addFormData.amount} onChange={(e) => setAddFormData({ ...addFormData, amount: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Due Days" value={addFormData.due_days} onChange={(e) => setAddFormData({ ...addFormData, due_days: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <Button onClick={handleAdd} className="bg-green-600 text-white hover:bg-green-700">Save</Button>
              <Button onClick={() => setShowAddForm(false)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">Cancel</Button>
            </div>
          )}
        </div>
      )}
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          {data.items.map((item) => (
            <Card key={item.id} className="space-y-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  {editingFee === item.id ? (
                    <input type="text" defaultValue={item.termName} onChange={(e) => setEditFormData({ ...editFormData, term_name: e.target.value })} className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white" />
                  ) : (
                    <p className="text-sm text-[#9eb1cf]">{item.termName}</p>
                  )}
                  {editingFee === item.id ? (
                    <input type="text" defaultValue={item.title} onChange={(e) => setEditFormData({ ...editFormData, title: e.target.value })} className="mt-2 rounded border border-white/20 bg-white/10 px-2 py-1 text-2xl font-semibold text-white" />
                  ) : (
                    <p className="mt-2 text-2xl font-semibold text-white">{item.title}</p>
                  )}
                </div>
                <div className="flex gap-2 items-center">
                  {editingFee === item.id ? (
                    <>
                      <Button size="sm" onClick={() => handleSaveEdit(item.id)} className="bg-green-600 text-white hover:bg-green-700"><Save className="h-4 w-4" /></Button>
                      <Button size="sm" onClick={handleCancelEdit} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><X className="h-4 w-4" /></Button>
                    </>
                  ) : (
                    <>
                      {canEdit && <Button size="sm" onClick={() => handleEdit(item)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><Edit className="h-4 w-4" /></Button>}
                      {canDelete && <Button size="sm" onClick={() => handleDelete(item.id)} variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10"><Trash2 className="h-4 w-4" /></Button>}
                    </>
                  )}
                  <Badge tone="neutral">{item.dueDays} days</Badge>
                </div>
              </div>
              <p className="text-sm leading-7 text-[#d6dfef]">Class: {item.className}</p>
              {editingFee === item.id ? (
                <input type="text" defaultValue={item.amount} onChange={(e) => setEditFormData({ ...editFormData, amount: e.target.value })} className="text-3xl font-serif text-[#f9d28a] rounded border border-white/20 bg-white/10 px-2 py-1" />
              ) : (
                <p className="text-3xl font-serif text-[#f9d28a]">{item.amount}</p>
              )}
              <div className="text-sm text-[#9eb1cf]">
                Fee bundles are used for invoice generation and debtor follow-up.
              </div>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  );
}

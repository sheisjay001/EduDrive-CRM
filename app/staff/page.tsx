"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DataTable, LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useStaffQuery } from "@/hooks/use-crm-query";
import { Edit, Trash2, Save, X, Plus } from "lucide-react";
import { getUser, getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function StaffPage() {
  const { data, isLoading, refetch } = useStaffQuery();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingStaff, setEditingStaff] = useState<number | null>(null);
  const [editFormData, setEditFormData] = useState({});
  const [addFormData, setAddFormData] = useState({ full_name: "", email: "", role: "", phone: "" });

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";
  const canEdit = ["school_admin", "super_admin"].includes(userRole);
  const canDelete = userRole === "super_admin";

  const handleEdit = (staff: { name: string; role: string; attendance: string; responseTime: string; performance: string; email?: string; phone?: string }, index: number) => {
    setEditingStaff(index);
    setEditFormData({ full_name: staff.name, email: staff.email, role: staff.role, phone: staff.phone });
  };

  const handleSaveEdit = async () => {
    try {
      // TODO: Implement proper API call when backend has staff update endpoint
      // const response = await fetch(`${API_URL}/staff/${staffId}`, {
      //   method: "PATCH",
      //   headers: { "Content-Type": "application/json", Authorization: `Bearer ${getAccessToken()}` },
      //   body: JSON.stringify(editFormData),
      // });
      // if (response.ok) { setEditingStaff(null); refetch(); alert("Staff updated"); }
      setEditingStaff(null);
      alert("Staff updated (demo mode)");
    } catch { alert("Error updating staff"); }
  };

  const handleCancelEdit = () => { setEditingStaff(null); setEditFormData({}); };

  const handleDelete = async () => {
    if (!confirm("Delete this staff member?")) return;
    try {
      // TODO: Implement proper API call when backend has staff delete endpoint
      // const response = await fetch(`${API_URL}/staff/${staffId}`, {
      //   method: "DELETE",
      //   headers: { Authorization: `Bearer ${getAccessToken()}` },
      // });
      // if (response.ok) { refetch(); alert("Staff deleted"); }
      refetch();
      alert("Staff deleted (demo mode)");
    } catch { alert("Error deleting staff"); }
  };

  const handleAdd = async () => {
    try {
      const response = await fetch(`${API_URL}/staff`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${getAccessToken()}` },
        body: JSON.stringify(addFormData),
      });
      if (response.ok) { setShowAddForm(false); setAddFormData({ full_name: "", email: "", role: "", phone: "" }); refetch(); alert("Staff created"); }
    } catch { alert("Error creating staff"); }
  };

  return (
    <AppShell
      eyebrow="Staff Operations"
      title="Attendance, responsiveness, and accountability"
      description="Give school leaders a simple view of who is showing up, who is responding quickly, and where operational performance is strongest."
    >
      {canEdit && (
        <div className="mb-6">
          {!showAddForm ? (
            <Button onClick={() => setShowAddForm(true)} className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
              <Plus className="h-4 w-4 mr-2" /> Add Staff
            </Button>
          ) : (
            <div className="flex gap-2 items-center flex-wrap">
              <input type="text" placeholder="Full Name" value={addFormData.full_name} onChange={(e) => setAddFormData({ ...addFormData, full_name: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="email" placeholder="Email" value={addFormData.email} onChange={(e) => setAddFormData({ ...addFormData, email: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Role" value={addFormData.role} onChange={(e) => setAddFormData({ ...addFormData, role: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <input type="text" placeholder="Phone" value={addFormData.phone} onChange={(e) => setAddFormData({ ...addFormData, phone: e.target.value })} className="rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none" />
              <Button onClick={handleAdd} className="bg-green-600 text-white hover:bg-green-700">Save</Button>
              <Button onClick={() => setShowAddForm(false)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">Cancel</Button>
            </div>
          )}
        </div>
      )}
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="grid gap-4 xl:grid-cols-3">
            {data.metrics.map((metric) => (
              <Card key={metric.label}>
                <p className="text-sm font-semibold text-white">{metric.label}</p>
                <p className="mt-4 font-serif text-4xl text-[#f9d28a]">{metric.value}</p>
                <p className="mt-3 text-sm text-[#9eb1cf]">{metric.note}</p>
              </Card>
            ))}
          </div>
          <DataTable
            title="Staff watchlist"
            description="Daily visibility into service posture and operational consistency."
            columns={["Name", "Role", "Attendance", "Response time", "Performance signal", "Actions"]}
            rows={data.people.map((person, index) => [
              editingStaff === index ? (
                <input type="text" defaultValue={person.name} onChange={(e) => setEditFormData({ ...editFormData, full_name: e.target.value })} className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white" />
              ) : (
                person.name
              ),
              editingStaff === index ? (
                <input type="text" defaultValue={person.role} onChange={(e) => setEditFormData({ ...editFormData, role: e.target.value })} className="rounded border border-white/20 bg-white/10 px-2 py-1 text-sm text-white" />
              ) : (
                <Badge tone="neutral">{person.role}</Badge>
              ),
              person.attendance,
              person.responseTime,
              person.performance,
              <div key={`person-${index}-actions`} className="flex gap-2">
                {editingStaff === index ? (
                  <>
                    <Button size="sm" onClick={() => handleSaveEdit()} className="bg-green-600 text-white hover:bg-green-700"><Save className="h-4 w-4" /></Button>
                    <Button size="sm" onClick={handleCancelEdit} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><X className="h-4 w-4" /></Button>
                  </>
                ) : (
                  <>
                    {canEdit && <Button size="sm" onClick={() => handleEdit(person, index)} variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"><Edit className="h-4 w-4" /></Button>}
                    {canDelete && <Button size="sm" onClick={() => handleDelete()} variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10"><Trash2 className="h-4 w-4" /></Button>}
                  </>
                )}
              </div>,
            ])}
          />
        </>
      )}
    </AppShell>
  );
}

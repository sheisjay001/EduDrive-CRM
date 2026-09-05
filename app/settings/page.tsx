"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useSettingsQuery } from "@/hooks/use-crm-query";
import { getUser } from "@/services/auth-storage";
import { CreditCard, Plus, Trash2, Lock } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

export default function SettingsPage() {
  const { data, isLoading, refetch } = useSettingsQuery();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    primary_color: "",
    logo_url: "",
    school_type: "",
    paystack_public_key: "",
    paystack_secret_key: "",
    flutterwave_public_key: "",
    flutterwave_secret_key: "",
    brevo_api_key: "",
    termii_api_key: "",
    whatsapp_phone_number_id: "",
    whatsapp_access_token: "",
  } as Record<string, string>);

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";

  const handleEdit = () => {
    if (data) {
      setFormData({
        name: data.groups[0]?.items[0]?.value || "",
        primary_color: data.groups[0]?.items[1]?.value || "",
        logo_url: data.groups[0]?.items[2]?.value || "",
        school_type: data.groups[0]?.items[3]?.value || "",
        paystack_public_key: data.groups[1]?.items[0]?.value || "",
        paystack_secret_key: data.groups[1]?.items[1]?.value || "",
        flutterwave_public_key: data.groups[1]?.items[2]?.value || "",
        flutterwave_secret_key: data.groups[1]?.items[3]?.value || "",
        brevo_api_key: data.groups[2]?.items[0]?.value || "",
        termii_api_key: data.groups[2]?.items[1]?.value || "",
        whatsapp_phone_number_id: data.groups[2]?.items[2]?.value || "",
        whatsapp_access_token: data.groups[2]?.items[3]?.value || "",
      });
      setIsEditing(true);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch(`${API_URL}/settings`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setIsEditing(false);
        refetch();
      } else {
        alert("Failed to save settings");
      }
    } catch {
      alert("Error saving settings");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  return (
    <AppShell
      eyebrow="School Settings"
      title="Brand, billing, and channel configuration"
      description="Set the school's identity, payment providers, sender profiles, and academic structure from a configuration space built for administrators."
    >
      {isLoading || !data ? (
        <LoadingPanel />
      ) : (
        <>
          {userRole === "school_admin" && (
            <div className="mb-6 flex justify-end">
              {!isEditing ? (
                <Button
                  onClick={handleEdit}
                  className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
                >
                  Edit Settings
                </Button>
              ) : (
                <div className="flex gap-2">
                  <Button
                    onClick={handleCancel}
                    variant="outline"
                    className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
                  >
                    {isSaving ? "Saving..." : "Save Changes"}
                  </Button>
                </div>
              )}
            </div>
          )}
          <div className="grid gap-6 xl:grid-cols-3">
            {data.groups.map((group) => (
              <Card key={group.title}>
                <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">{group.title}</p>
                <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">{group.description}</p>
                <div className="mt-6 space-y-4">
                  {group.items.map((item) => (
                    <div key={item.label} className="rounded-[24px] border border-white/10 bg-white/5 p-4">
                      <p className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">{item.label}</p>
                      {isEditing && userRole === "school_admin" && (
                        <input
                          type="text"
                          value={formData[item.label.toLowerCase().replace(/ /g, "_")] || item.value}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              [item.label.toLowerCase().replace(/ /g, "_")]: e.target.value,
                            })
                          }
                          className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                        />
                      )}
                      {!isEditing && <p className="mt-2 text-sm font-medium text-white">{item.value}</p>}
                    </div>
                  ))}
                </div>
              </Card>
            ))}

            <Card className="p-6">
              <p className="text-xs uppercase tracking-[0.35em] text-[#d9a441]">Scratch Card PINs</p>
              <p className="mt-3 text-sm leading-7 text-[#9eb1cf]">Generate and manage PINs for result verification</p>
              <div className="mt-6 space-y-4">
                <Button className="w-full bg-[#d9a441] text-white hover:bg-[#d9a441]/90">
                  <Plus className="mr-2 h-4 w-4" />
                  Generate PINs
                </Button>
                <div className="space-y-2">
                  {[
                    { code: "1234-5678-90", serial: "SN-001", status: "unused" },
                    { code: "2345-6789-01", serial: "SN-002", status: "used" },
                    { code: "3456-7890-12", serial: "SN-003", status: "blocked" },
                  ].map((pin, idx) => (
                    <div key={idx} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-3">
                      <div>
                        <p className="text-sm font-medium text-white">{pin.code}</p>
                        <p className="text-xs text-[#9eb1cf]">{pin.serial}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs ${
                          pin.status === "unused" ? "text-green-400" :
                          pin.status === "used" ? "text-yellow-400" : "text-red-400"
                        }`}>{pin.status}</span>
                        {pin.status === "unused" && (
                          <Button size="sm" variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                            <Lock className="h-3 w-3" />
                          </Button>
                        )}
                        <Button size="sm" variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}

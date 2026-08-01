"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useSettingsQuery } from "@/hooks/use-crm-query";
import { getUser } from "@/services/auth-storage";

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
    } catch (error) {
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
          </div>
        </>
      )}
    </AppShell>
  );
}

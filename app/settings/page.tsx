"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { useSettingsQuery, usePinsQuery } from "@/hooks/use-crm-query";
import { getUser } from "@/services/auth-storage";
import { Plus, Trash2, Lock, X, Save } from "lucide-react";
import { apiClient } from "@/services/api-client";
import type { PINItem } from "@/types/crm";

const LABEL_TO_KEY: Record<string, string> = {
  "School Name": "name",
  "Primary Color": "primary_color",
  "Logo URL": "logo_url",
  "School Type": "school_type",
  "Paystack Public Key": "paystack_public_key",
  "Paystack Secret Key": "paystack_secret_key",
  "Flutterwave Public Key": "flutterwave_public_key",
  "Flutterwave Secret Key": "flutterwave_secret_key",
  "Brevo API Key": "brevo_api_key",
  "Termii API Key": "termii_api_key",
  "WhatsApp Phone Number ID": "whatsapp_phone_number_id",
  "WhatsApp Access Token": "whatsapp_access_token",
};

export default function SettingsPage() {
  const { data, isLoading, refetch: refetchSettings } = useSettingsQuery();
  const { data: pinsData, isLoading: pinsLoading, refetch: refetchPins } = usePinsQuery();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showGeneratePinForm, setShowGeneratePinForm] = useState(false);
  const [pinQuantity, setPinQuantity] = useState(10);
  const [isGeneratingPins, setIsGeneratingPins] = useState(false);
  const [formData, setFormData] = useState<Record<string, string>>({
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
  });

  const user = getUser();
  const userRole = (user as { role?: string })?.role || "school_admin";

  const pins: PINItem[] = Array.isArray(pinsData as unknown as PINItem[])
    ? (pinsData as unknown as PINItem[])
    : (pinsData as { pins?: PINItem[] } | undefined)?.pins ?? [];

  const handleEdit = () => {
    if (data) {
      const next: Record<string, string> = { ...formData };
      data.groups.forEach((group) => {
        group.items.forEach((item) => {
          const key = LABEL_TO_KEY[item.label];
          if (key) {
            next[key] = item.value ?? "";
          }
        });
      });
      setFormData(next);
      setIsEditing(true);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await apiClient.updateSettings(formData as unknown as Record<string, unknown>);
      setIsEditing(false);
      await refetchSettings();
      alert("Settings saved successfully");
    } catch {
      alert("Error saving settings");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  const handleGeneratePins = async () => {
    if (pinQuantity < 1 || pinQuantity > 100) {
      alert("Quantity must be between 1 and 100");
      return;
    }
    setIsGeneratingPins(true);
    try {
      await apiClient.generatePins({ quantity: pinQuantity });
      alert(`Successfully generated ${pinQuantity} PIN(s)`);
      setShowGeneratePinForm(false);
      setPinQuantity(10);
      await refetchPins();
    } catch {
      alert("Error generating PINs");
    } finally {
      setIsGeneratingPins(false);
    }
  };

  const handleBlockPin = async (pinId: number, serial: string) => {
    if (!confirm(`Are you sure you want to block PIN with serial ${serial}?`)) return;
    try {
      await apiClient.blockPin(pinId);
      alert("PIN blocked successfully");
      await refetchPins();
    } catch {
      alert("Error blocking PIN");
    }
  };

  const handleDeletePin = async (pinId: number, serial: string) => {
    if (!confirm(`Are you sure you want to delete PIN with serial ${serial}?`)) return;
    try {
      await apiClient.deletePin(pinId);
      alert("PIN deleted successfully");
      await refetchPins();
    } catch {
      alert("Error deleting PIN");
    }
  };

  const handleFieldChange = (label: string, value: string) => {
    const key = LABEL_TO_KEY[label];
    if (!key) return;
    setFormData({ ...formData, [key]: value });
  };

  const resolveFormValue = (label: string, fallbackValue: string): string => {
    const key = LABEL_TO_KEY[label];
    if (!key) return fallbackValue;
    return formData[key] ?? fallbackValue;
  };

  return (
    <AppShell
      eyebrow="School Settings"
      title="Brand, billing, and channel configuration"
      description="Set the school&apos;s identity, payment providers, sender profiles, and academic structure from a configuration space built for administrators."
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
                    <Save className="mr-2 h-4 w-4" />
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
                          value={resolveFormValue(item.label, item.value)}
                          onChange={(e) => handleFieldChange(item.label, e.target.value)}
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
                <div className="flex gap-2">
                  <Button
                    onClick={() => setShowGeneratePinForm((v) => !v)}
                    className="flex-1 bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Generate PINs
                  </Button>
                </div>

                {showGeneratePinForm && (
                  <div className="rounded-[24px] border border-white/10 bg-white/5 p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <p className="text-sm font-semibold text-white">Batch Generate</p>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setShowGeneratePinForm(false)}
                        className="border-white/20 text-[#9eb1cf]"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="mb-3">
                      <label className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Quantity (1-100)</label>
                      <input
                        type="number"
                        min={1}
                        max={100}
                        value={pinQuantity}
                        onChange={(e) => setPinQuantity(Number(e.target.value))}
                        className="mt-2 w-full rounded-lg border border-white/20 bg-white/10 px-3 py-2 text-sm text-white focus:border-[#d9a441] focus:outline-none"
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="outline"
                        onClick={() => setShowGeneratePinForm(false)}
                        className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10"
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={handleGeneratePins}
                        disabled={isGeneratingPins}
                        className="bg-[#d9a441] text-white hover:bg-[#d9a441]/90"
                      >
                        {isGeneratingPins ? "Generating..." : "Confirm"}
                      </Button>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  {pinsLoading ? (
                    <p className="text-center text-sm text-[#9eb1cf]">Loading PINs…</p>
                  ) : pins.length === 0 ? (
                    <p className="text-center text-sm text-[#9eb1cf]">No PINs generated yet</p>
                  ) : (
                    pins.map((pin) => (
                      <div key={pin.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-3">
                        <div>
                          <p className="text-sm font-medium text-white">{pin.pin_code}</p>
                          <p className="text-xs text-[#9eb1cf]">{pin.serial_number} • {pin.usage_count}/{pin.max_usage} uses</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs ${
                            pin.status === "unused" ? "text-green-400" :
                            pin.status === "used" ? "text-yellow-400" : "text-red-400"
                          }`}>{pin.status}</span>
                          {pin.status === "unused" && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleBlockPin(pin.id, pin.serial_number)}
                              className="border-red-500/30 text-red-500 hover:bg-red-500/10"
                              title="Block PIN"
                            >
                              <Lock className="h-3 w-3" />
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeletePin(pin.id, pin.serial_number)}
                            className="border-red-500/30 text-red-500 hover:bg-red-500/10"
                            title="Delete PIN"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </Card>
          </div>
        </>
      )}
    </AppShell>
  );
}

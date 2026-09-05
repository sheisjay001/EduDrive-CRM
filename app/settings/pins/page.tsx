"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Plus, Trash2, Ban, Download, Copy } from "lucide-react";

interface PIN {
  id: number;
  pin_code: string;
  serial_number: string;
  status: string;
  student_id: number | null;
  usage_count: number;
  max_usage: number;
  created_at: string;
}

export default function PINManagementPage() {
  const [pins, setPins] = useState<PIN[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showGenerate, setShowGenerate] = useState(false);
  const [quantity, setQuantity] = useState(10);
  const [activeTab, setActiveTab] = useState("all");

  const fetchPins = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/pins", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPins(data);
      }
    } catch (error) {
      console.error("Failed to fetch PINs:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/pins/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({ quantity })
      });
      if (response.ok) {
        setShowGenerate(false);
        setQuantity(10);
        fetchPins();
      }
    } catch (error) {
      console.error("Failed to generate PINs:", error);
    }
  };

  const handleDelete = async (pinId: number) => {
    if (!confirm("Are you sure you want to delete this PIN?")) return;
    try {
      const response = await fetch(`/api/pins/${pinId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        fetchPins();
      }
    } catch (error) {
      console.error("Failed to delete PIN:", error);
    }
  };

  const handleBlock = async (pinId: number) => {
    try {
      const response = await fetch(`/api/pins/${pinId}/block`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        fetchPins();
      }
    } catch (error) {
      console.error("Failed to block PIN:", error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatPIN = (pin: string) => {
    return pin.replace(/(\d{4})(\d{4})(\d{4})/, "$1-$2-$3");
  };

  useState(() => {
    fetchPins();
  });

  const unusedCount = pins.filter(p => p.status === "unused").length;
  const usedCount = pins.filter(p => p.status === "used").length;
  const blockedCount = pins.filter(p => p.status === "blocked").length;

  return (
    <AppShell
      eyebrow="Settings"
      title="Scratch Card PIN Management"
      description="Generate and manage scratch card PINs for result checking"
    >
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="p-6">
            <p className="text-sm text-gray-400">Total PINs</p>
            <p className="text-3xl font-bold text-white mt-2">{pins.length}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">Unused</p>
            <p className="text-3xl font-bold text-green-400 mt-2">{unusedCount}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">Used</p>
            <p className="text-3xl font-bold text-blue-400 mt-2">{usedCount}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">Blocked</p>
            <p className="text-3xl font-bold text-red-400 mt-2">{blockedCount}</p>
          </Card>
        </div>

        {/* Generate Button */}
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-semibold text-white">All PINs</h3>
          <Button onClick={() => setShowGenerate(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Generate PINs
          </Button>
        </div>

        <Dialog open={showGenerate} onOpenChange={setShowGenerate}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Generate Scratch Card PINs</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <Label htmlFor="quantity">Quantity (1-100)</Label>
                <Input
                  id="quantity"
                  type="number"
                  min="1"
                  max="100"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value))}
                  required
                />
              </div>
              <Button type="submit" className="w-full">Generate PINs</Button>
            </form>
          </DialogContent>
        </Dialog>

        {/* PINs Table */}
        {isLoading ? (
          <Card className="p-6">
            <p className="text-center text-gray-400">Loading PINs...</p>
          </Card>
        ) : (
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Serial Number</th>
                    <th className="text-left p-4 text-sm font-medium text-gray-400">PIN Code</th>
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Status</th>
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Usage</th>
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Created</th>
                    <th className="text-left p-4 text-sm font-medium text-gray-400">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {pins.map((pin) => (
                    <tr key={pin.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <code className="text-sm text-white">{pin.serial_number}</code>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(pin.serial_number)}
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <code className="text-sm text-white">{formatPIN(pin.pin_code)}</code>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(pin.pin_code)}
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge
                          tone={
                            pin.status === "unused" ? "good" :
                            pin.status === "used" ? "neutral" :
                            "danger"
                          }
                        >
                          {pin.status}
                        </Badge>
                      </td>
                      <td className="p-4 text-sm text-gray-400">
                        {pin.usage_count}/{pin.max_usage}
                      </td>
                      <td className="p-4 text-sm text-gray-400">
                        {new Date(pin.created_at).toLocaleDateString()}
                      </td>
                      <td className="p-4">
                        <div className="flex gap-2">
                          {pin.status !== "blocked" && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleBlock(pin.id)}
                            >
                              <Ban className="w-4 h-4" />
                            </Button>
                          )}
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(pin.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {pins.length === 0 && (
              <div className="p-12 text-center">
                <p className="text-gray-400">No PINs generated yet. Click "Generate PINs" to get started.</p>
              </div>
            )}
          </Card>
        )}
      </div>
    </AppShell>
  );
}

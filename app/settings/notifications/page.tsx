"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Plus, Trash2, Bell, Users } from "lucide-react";

interface Notification {
  id: number;
  title: string;
  message: string;
  target_audience: string;
  created_at: string;
}

export default function NotificationsManagementPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);

  const [newNotification, setNewNotification] = useState({
    title: "",
    message: "",
    target_audience: "all"
  });

  const fetchNotifications = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/notifications", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      }
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/notifications", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify(newNotification)
      });
      if (response.ok) {
        setShowCreate(false);
        setNewNotification({ title: "", message: "", target_audience: "all" });
        fetchNotifications();
      }
    } catch (error) {
      console.error("Failed to create notification:", error);
    }
  };

  const handleDelete = async (notificationId: number) => {
    if (!confirm("Are you sure you want to delete this notification?")) return;
    try {
      const response = await fetch(`/api/notifications/${notificationId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        fetchNotifications();
      }
    } catch (error) {
      console.error("Failed to delete notification:", error);
    }
  };

  useState(() => {
    fetchNotifications();
  });

  const allCount = notifications.filter(n => n.target_audience === "all").length;
  const studentCount = notifications.filter(n => n.target_audience === "student").length;
  const teacherCount = notifications.filter(n => n.target_audience === "teacher").length;
  const parentCount = notifications.filter(n => n.target_audience === "parent").length;

  const getAudienceColor = (audience: string) => {
    switch (audience) {
      case "all": return "text-blue-400";
      case "student": return "text-green-400";
      case "teacher": return "text-purple-400";
      case "parent": return "text-yellow-400";
      case "admin": return "text-red-400";
      default: return "text-gray-400";
    }
  };

  return (
    <AppShell
      eyebrow="Settings"
      title="Notifications"
      description="Create and manage school-wide notifications"
    >
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-5">
          <Card className="p-6">
            <p className="text-sm text-gray-400">Total</p>
            <p className="text-3xl font-bold text-white mt-2">{notifications.length}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">All</p>
            <p className="text-3xl font-bold text-blue-400 mt-2">{allCount}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">Students</p>
            <p className="text-3xl font-bold text-green-400 mt-2">{studentCount}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">Teachers</p>
            <p className="text-3xl font-bold text-purple-400 mt-2">{teacherCount}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">Parents</p>
            <p className="text-3xl font-bold text-yellow-400 mt-2">{parentCount}</p>
          </Card>
        </div>

        {/* Create Button */}
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-semibold text-white">All Notifications</h3>
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create Notification
          </Button>
        </div>

        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Notification</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={newNotification.title}
                  onChange={(e) => setNewNotification({ ...newNotification, title: e.target.value })}
                  placeholder="Notification title"
                  required
                />
              </div>
              <div>
                <Label htmlFor="message">Message</Label>
                <Textarea
                  id="message"
                  value={newNotification.message}
                  onChange={(e) => setNewNotification({ ...newNotification, message: e.target.value })}
                  placeholder="Notification message"
                  required
                />
              </div>
              <div>
                <Label htmlFor="audience">Target Audience</Label>
                <Select 
                  id="audience"
                  value={newNotification.target_audience} 
                  onChange={(e) => setNewNotification({ ...newNotification, target_audience: e.target.value })}
                >
                  <option value="all">All Users</option>
                  <option value="student">Students Only</option>
                  <option value="teacher">Teachers Only</option>
                  <option value="parent">Parents Only</option>
                  <option value="admin">Admins Only</option>
                </Select>
              </div>
              <Button type="submit" className="w-full">Create Notification</Button>
            </form>
          </DialogContent>
        </Dialog>

        {/* Notifications List */}
        {isLoading ? (
          <Card className="p-6">
            <p className="text-center text-gray-400">Loading notifications...</p>
          </Card>
        ) : (
          <div className="grid gap-4">
            {notifications.map((notification) => (
              <Card key={notification.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center">
                      <Bell className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-lg font-semibold text-white">{notification.title}</h4>
                        <Badge tone="neutral" className={getAudienceColor(notification.target_audience)}>
                          {notification.target_audience}
                        </Badge>
                      </div>
                      <p className="text-gray-400 mb-2">{notification.message}</p>
                      <p className="text-xs text-gray-500">
                        Created: {new Date(notification.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(notification.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            ))}
            {notifications.length === 0 && (
              <Card className="p-12 text-center">
                <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-400">No notifications created yet. Click "Create Notification" to get started.</p>
              </Card>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}

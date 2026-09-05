"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Plus, Trash2, Download, FileText, Calendar } from "lucide-react";

interface Timetable {
  id: number;
  title: string;
  file_path: string;
  type: string;
  class: string;
  session: string;
  term: string;
  uploaded_at: string;
}

export default function TimetableManagementPage() {
  const [timetables, setTimetables] = useState<Timetable[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [newTimetable, setNewTimetable] = useState({
    title: "",
    type: "class",
    class: "all",
    session: "",
    term: ""
  });

  const fetchTimetables = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/timetables", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setTimetables(data);
      }
    } catch (error) {
      console.error("Failed to fetch timetables:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("title", newTimetable.title);
    formData.append("type", newTimetable.type);
    formData.append("class", newTimetable.class);
    formData.append("session", newTimetable.session);
    formData.append("term", newTimetable.term);
    formData.append("file", selectedFile);

    try {
      const response = await fetch("/api/timetables", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: formData
      });
      if (response.ok) {
        setShowUpload(false);
        setNewTimetable({ title: "", type: "class", class: "all", session: "", term: "" });
        setSelectedFile(null);
        fetchTimetables();
      }
    } catch (error) {
      console.error("Failed to upload timetable:", error);
    }
  };

  const handleDelete = async (timetableId: number) => {
    if (!confirm("Are you sure you want to delete this timetable?")) return;
    try {
      const response = await fetch(`/api/timetables/${timetableId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        fetchTimetables();
      }
    } catch (error) {
      console.error("Failed to delete timetable:", error);
    }
  };

  useState(() => {
    fetchTimetables();
  });

  const examCount = timetables.filter(t => t.type === "exam").length;
  const classCount = timetables.filter(t => t.type === "class").length;
  const generalCount = timetables.filter(t => t.type === "general").length;

  return (
    <AppShell
      eyebrow="Settings"
      title="Timetable Management"
      description="Upload and manage school timetables (exam, class, general)"
    >
      <div className="space-y-6">
        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="p-6">
            <p className="text-sm text-gray-400">Total Timetables</p>
            <p className="text-3xl font-bold text-white mt-2">{timetables.length}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">Exam</p>
            <p className="text-3xl font-bold text-purple-400 mt-2">{examCount}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">Class</p>
            <p className="text-3xl font-bold text-blue-400 mt-2">{classCount}</p>
          </Card>
          <Card className="p-6">
            <p className="text-sm text-gray-400">General</p>
            <p className="text-3xl font-bold text-green-400 mt-2">{generalCount}</p>
          </Card>
        </div>

        {/* Upload Button */}
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-semibold text-white">All Timetables</h3>
          <Button onClick={() => setShowUpload(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Upload Timetable
          </Button>
        </div>

        <Dialog open={showUpload} onOpenChange={setShowUpload}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload Timetable</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={newTimetable.title}
                  onChange={(e) => setNewTimetable({ ...newTimetable, title: e.target.value })}
                  placeholder="e.g., JSS1 First Term Timetable"
                  required
                />
              </div>
              <div>
                <Label htmlFor="type">Type</Label>
                <Select 
                  id="type"
                  value={newTimetable.type} 
                  onChange={(e) => setNewTimetable({ ...newTimetable, type: e.target.value })}
                >
                  <option value="class">Class Timetable</option>
                  <option value="exam">Exam Timetable</option>
                  <option value="general">General Timetable</option>
                </Select>
              </div>
              <div>
                <Label htmlFor="class">Class (leave empty for all)</Label>
                <Input
                  id="class"
                  value={newTimetable.class}
                  onChange={(e) => setNewTimetable({ ...newTimetable, class: e.target.value })}
                  placeholder="e.g., JSS1, SS2, or leave empty for all"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="session">Session</Label>
                  <Input
                    id="session"
                    value={newTimetable.session}
                    onChange={(e) => setNewTimetable({ ...newTimetable, session: e.target.value })}
                    placeholder="e.g., 2024/2025"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="term">Term</Label>
                  <Input
                    id="term"
                    value={newTimetable.term}
                    onChange={(e) => setNewTimetable({ ...newTimetable, term: e.target.value })}
                    placeholder="e.g., First Term"
                    required
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="file">File (PDF, JPG, PNG)</Label>
                <Input
                  id="file"
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  required
                />
              </div>
              <Button type="submit" className="w-full">Upload Timetable</Button>
            </form>
          </DialogContent>
        </Dialog>

        {/* Timetables Grid */}
        {isLoading ? (
          <Card className="p-6">
            <p className="text-center text-gray-400">Loading timetables...</p>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {timetables.map((timetable) => (
              <Card key={timetable.id} className="p-6">
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-5 h-5 text-blue-400" />
                        <h4 className="text-lg font-semibold text-white">{timetable.title}</h4>
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-sm text-gray-400">
                          <Badge tone={
                            timetable.type === "exam" ? "warn" :
                            timetable.type === "class" ? "neutral" :
                            "good"
                          }>
                            {timetable.type}
                          </Badge>
                          <span>•</span>
                          <span>{timetable.class === "all" ? "All Classes" : timetable.class}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-400">
                          <Calendar className="w-4 h-4" />
                          <span>{timetable.session} • {timetable.term}</span>
                        </div>
                        <p className="text-xs text-gray-500">
                          Uploaded: {new Date(timetable.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Download className="w-4 h-4 mr-1" />
                      View
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(timetable.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
            {timetables.length === 0 && (
              <Card className="p-12 col-span-full text-center">
                <p className="text-gray-400">No timetables uploaded yet. Click "Upload Timetable" to get started.</p>
              </Card>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}

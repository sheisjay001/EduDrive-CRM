"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Users, Calendar, Upload, CheckCircle, XCircle } from "lucide-react";

interface Student {
  id: number;
  full_name: string;
  admission_no: string;
  student_class: string;
  gender: string;
  parent_phone: string;
}

interface Attendance {
  id: number;
  student_id: number;
  student_name: string;
  admission_no: string;
  student_class: string;
  date: string;
  status: string;
  remark: string;
}

export default function TeacherFunctionsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [attendance, setAttendance] = useState<Attendance[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("students");
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [showBulkAttendance, setShowBulkAttendance] = useState(false);
  const [showUploadResults, setShowUploadResults] = useState(false);
  const [csvFile, setCsvFile] = useState<File | null>(null);

  const fetchStudents = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/teacher/my-students", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStudents(data);
      }
    } catch (error) {
      console.error("Failed to fetch students:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchAttendance = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/teacher/attendance?filter_date=${selectedDate}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAttendance(data);
      }
    } catch (error) {
      console.error("Failed to fetch attendance:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAttendance = async (studentId: number, status: string) => {
    try {
      const response = await fetch("/api/teacher/attendance", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          student_id: studentId,
          date: selectedDate,
          status: status
        })
      });
      if (response.ok) {
        fetchAttendance();
      }
    } catch (error) {
      console.error("Failed to mark attendance:", error);
    }
  };

  const handleBulkAttendance = async () => {
    const attendanceRecords = students.map(s => ({
      student_id: s.id,
      status: "present"
    }));

    try {
      const response = await fetch("/api/teacher/attendance/bulk", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          date: selectedDate,
          attendance_records: attendanceRecords
        })
      });
      if (response.ok) {
        setShowBulkAttendance(false);
        fetchAttendance();
      }
    } catch (error) {
      console.error("Failed to mark bulk attendance:", error);
    }
  };

  const handleUploadResults = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!csvFile) {
      alert("Please select a CSV file");
      return;
    }

    const formData = new FormData();
    formData.append("file", csvFile);

    try {
      const response = await fetch("/api/results/upload-csv", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: formData
      });
      if (response.ok) {
        setShowUploadResults(false);
        setCsvFile(null);
        alert("Results uploaded successfully!");
      }
    } catch (error) {
      console.error("Failed to upload results:", error);
    }
  };

  useState(() => {
    fetchStudents();
    fetchAttendance();
  });

  const presentCount = attendance.filter(a => a.status === "present").length;
  const absentCount = attendance.filter(a => a.status === "absent").length;
  const lateCount = attendance.filter(a => a.status === "late").length;

  return (
    <AppShell
      eyebrow="Teacher Dashboard"
      title="My Functions"
      description="Manage your students, attendance, and results"
    >
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="students">My Students</TabsTrigger>
          <TabsTrigger value="attendance">Attendance</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="students" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-semibold text-white">Assigned Students</h3>
            <Badge tone="neutral">{students.length} students</Badge>
          </div>

          {isLoading ? (
            <Card className="p-6">
              <p className="text-center text-gray-400">Loading students...</p>
            </Card>
          ) : (
            <div className="grid gap-4">
              {students.map((student) => (
                <Card key={student.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-semibold">
                        {student.full_name.charAt(0)}
                      </div>
                      <div>
                        <h4 className="text-white font-medium">{student.full_name}</h4>
                        <p className="text-sm text-gray-400">Admission No: {student.admission_no}</p>
                        <p className="text-sm text-gray-400">Class: {student.student_class}</p>
                        <p className="text-xs text-gray-500 mt-1">Parent: {student.parent_phone}</p>
                      </div>
                    </div>
                    <Badge tone="neutral">{student.gender}</Badge>
                  </div>
                </Card>
              ))}
              {students.length === 0 && (
                <Card className="p-12 text-center">
                  <p className="text-gray-400">No students assigned to you yet.</p>
                </Card>
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="attendance" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xl font-semibold text-white">Attendance</h3>
              <div className="flex gap-4 mt-2">
                <Badge tone="good">{presentCount} Present</Badge>
                <Badge tone="danger">{absentCount} Absent</Badge>
                <Badge tone="warn">{lateCount} Late</Badge>
              </div>
            </div>
            <div className="flex gap-2">
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="w-auto"
              />
              <Button onClick={() => fetchAttendance()}>Load</Button>
              <Button onClick={() => setShowBulkAttendance(true)}>
                <CheckCircle className="w-4 h-4 mr-2" />
                Mark All Present
              </Button>
            </div>
          </div>

          {isLoading ? (
            <Card className="p-6">
              <p className="text-center text-gray-400">Loading attendance...</p>
            </Card>
          ) : (
            <div className="grid gap-4">
              {attendance.map((record) => (
                <Card key={record.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-semibold">
                        {record.student_name.charAt(0)}
                      </div>
                      <div>
                        <h4 className="text-white font-medium">{record.student_name}</h4>
                        <p className="text-sm text-gray-400">{record.admission_no} • {record.student_class}</p>
                        {record.remark && (
                          <p className="text-xs text-gray-500 mt-1">Remark: {record.remark}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant={record.status === "present" ? "primary" : "outline"}
                        size="sm"
                        onClick={() => handleMarkAttendance(record.student_id, "present")}
                      >
                        Present
                      </Button>
                      <Button
                        variant={record.status === "absent" ? "primary" : "outline"}
                        size="sm"
                        onClick={() => handleMarkAttendance(record.student_id, "absent")}
                      >
                        Absent
                      </Button>
                      <Button
                        variant={record.status === "late" ? "primary" : "outline"}
                        size="sm"
                        onClick={() => handleMarkAttendance(record.student_id, "late")}
                      >
                        Late
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
              {attendance.length === 0 && (
                <Card className="p-12 text-center">
                  <p className="text-gray-400">No attendance records for this date.</p>
                </Card>
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="results" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-semibold text-white">Results Management</h3>
            <Button onClick={() => setShowUploadResults(true)}>
              <Upload className="w-4 h-4 mr-2" />
              Upload CSV
            </Button>
          </div>

          <Card className="p-12 text-center">
            <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-white mb-2">Upload Results via CSV</h4>
            <p className="text-gray-400 mb-4">
              Upload student results in CSV format. The file should include admission number, CA score, and exam score.
            </p>
            <Button onClick={() => setShowUploadResults(true)}>
              <Upload className="w-4 h-4 mr-2" />
              Upload CSV File
            </Button>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Bulk Attendance Dialog */}
      <Dialog open={showBulkAttendance} onOpenChange={setShowBulkAttendance}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Mark All Present</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-gray-400">
              This will mark all {students.length} students as present for {selectedDate}.
            </p>
            <div className="flex gap-4">
              <Button variant="outline" onClick={() => setShowBulkAttendance(false)} className="flex-1">
                Cancel
              </Button>
              <Button onClick={handleBulkAttendance} className="flex-1">
                Confirm
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Upload Results Dialog */}
      <Dialog open={showUploadResults} onOpenChange={setShowUploadResults}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Results CSV</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleUploadResults} className="space-y-4">
            <div>
              <Label htmlFor="csv">CSV File</Label>
              <Input
                id="csv"
                type="file"
                accept=".csv"
                onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                required
              />
              <p className="text-xs text-gray-500 mt-2">
                Format: admission_no, ca_score, exam_score
              </p>
            </div>
            <div className="flex gap-4">
              <Button variant="outline" onClick={() => setShowUploadResults(false)} className="flex-1">
                Cancel
              </Button>
              <Button type="submit" className="flex-1">
                Upload
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}

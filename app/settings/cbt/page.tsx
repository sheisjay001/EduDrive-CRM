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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Plus, Trash2, Edit, Play } from "lucide-react";

interface CBTExam {
  id: number;
  title: string;
  class: string;
  duration_minutes: number;
  status: string;
  created_at: string;
}

interface CBTQuestion {
  id: number;
  exam_id: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_option: string;
}

export default function CBTManagementPage() {
  const [exams, setExams] = useState<CBTExam[]>([]);
  const [questions, setQuestions] = useState<CBTQuestion[]>([]);
  const [selectedExam, setSelectedExam] = useState<CBTExam | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateExam, setShowCreateExam] = useState(false);
  const [showAddQuestion, setShowAddQuestion] = useState(false);
  const [activeTab, setActiveTab] = useState("exams");

  // New exam form state
  const [newExam, setNewExam] = useState({
    title: "",
    class: "",
    duration_minutes: 30,
    status: "active"
  });

  // New question form state
  const [newQuestion, setNewQuestion] = useState({
    exam_id: 0,
    question_text: "",
    option_a: "",
    option_b: "",
    option_c: "",
    option_d: "",
    correct_option: "a"
  });

  const fetchExams = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/cbt/exams", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setExams(data);
      }
    } catch (error) {
      console.error("Failed to fetch exams:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchQuestions = async (examId: number) => {
    try {
      const response = await fetch(`/api/cbt/exams/${examId}/questions`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setQuestions(data);
      }
    } catch (error) {
      console.error("Failed to fetch questions:", error);
    }
  };

  const handleCreateExam = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/cbt/exams", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify(newExam)
      });
      if (response.ok) {
        setShowCreateExam(false);
        setNewExam({ title: "", class: "", duration_minutes: 30, status: "active" });
        fetchExams();
      }
    } catch (error) {
      console.error("Failed to create exam:", error);
    }
  };

  const handleAddQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/cbt/questions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify(newQuestion)
      });
      if (response.ok) {
        setShowAddQuestion(false);
        setNewQuestion({
          exam_id: selectedExam?.id || 0,
          question_text: "",
          option_a: "",
          option_b: "",
          option_c: "",
          option_d: "",
          correct_option: "a"
        });
        if (selectedExam) fetchQuestions(selectedExam.id);
      }
    } catch (error) {
      console.error("Failed to add question:", error);
    }
  };

  const handleDeleteExam = async (examId: number) => {
    if (!confirm("Are you sure you want to delete this exam?")) return;
    try {
      const response = await fetch(`/api/cbt/exams/${examId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        fetchExams();
        if (selectedExam?.id === examId) {
          setSelectedExam(null);
          setQuestions([]);
        }
      }
    } catch (error) {
      console.error("Failed to delete exam:", error);
    }
  };

  const handleSelectExam = (exam: CBTExam) => {
    setSelectedExam(exam);
    setNewQuestion({ ...newQuestion, exam_id: exam.id });
    fetchQuestions(exam.id);
  };

  useState(() => {
    fetchExams();
  });

  return (
    <AppShell
      eyebrow="Settings"
      title="CBT Management"
      description="Create and manage computer-based tests for students"
    >
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="exams">Exams</TabsTrigger>
          <TabsTrigger value="questions">Questions</TabsTrigger>
        </TabsList>

        <TabsContent value="exams" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-semibold text-white">All Exams</h3>
            <Button onClick={() => setShowCreateExam(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Exam
            </Button>
          </div>

          <Dialog open={showCreateExam} onOpenChange={setShowCreateExam}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Exam</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateExam} className="space-y-4">
                <div>
                  <Label htmlFor="title">Exam Title</Label>
                  <Input
                    id="title"
                    value={newExam.title}
                    onChange={(e) => setNewExam({ ...newExam, title: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="class">Class</Label>
                  <Input
                    id="class"
                    value={newExam.class}
                    onChange={(e) => setNewExam({ ...newExam, class: e.target.value })}
                    placeholder="e.g., JSS1, SS2"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="duration">Duration (minutes)</Label>
                  <Input
                    id="duration"
                    type="number"
                    value={newExam.duration_minutes}
                    onChange={(e) => setNewExam({ ...newExam, duration_minutes: parseInt(e.target.value) })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select 
                    id="status"
                    value={newExam.status} 
                    onChange={(e) => setNewExam({ ...newExam, status: e.target.value })}
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="archived">Archived</option>
                  </Select>
                </div>
                <Button type="submit" className="w-full">Create Exam</Button>
              </form>
            </DialogContent>
          </Dialog>

          {isLoading ? (
            <Card className="p-6">
              <p className="text-center text-gray-400">Loading exams...</p>
            </Card>
          ) : (
            <div className="grid gap-4">
              {exams.map((exam) => (
                <Card key={exam.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-lg font-semibold text-white">{exam.title}</h4>
                        <Badge tone={exam.status === "active" ? "good" : "neutral"}>{exam.status}</Badge>
                      </div>
                      <p className="text-sm text-gray-400">Class: {exam.class} • Duration: {exam.duration_minutes} minutes</p>
                      <p className="text-xs text-gray-500 mt-1">Created: {new Date(exam.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleSelectExam(exam)}>
                        <Play className="w-4 h-4 mr-1" />
                        Questions
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleDeleteExam(exam.id)}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
              {exams.length === 0 && (
                <Card className="p-12 text-center">
                  <p className="text-gray-400">No exams created yet. Click "Create Exam" to get started.</p>
                </Card>
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="questions" className="space-y-6">
          {!selectedExam ? (
            <Card className="p-12 text-center">
              <p className="text-gray-400">Select an exam from the Exams tab to manage its questions</p>
            </Card>
          ) : (
            <>
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-xl font-semibold text-white">{selectedExam.title}</h3>
                  <p className="text-sm text-gray-400">Class: {selectedExam.class} • {questions.length} questions</p>
                </div>
                <Button onClick={() => setShowAddQuestion(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Question
                </Button>
              </div>

              <Dialog open={showAddQuestion} onOpenChange={setShowAddQuestion}>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Add Question</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleAddQuestion} className="space-y-4">
                      <div>
                        <Label htmlFor="question">Question</Label>
                        <Textarea
                          id="question"
                          value={newQuestion.question_text}
                          onChange={(e) => setNewQuestion({ ...newQuestion, question_text: e.target.value })}
                          required
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="option_a">Option A</Label>
                          <Input
                            id="option_a"
                            value={newQuestion.option_a}
                            onChange={(e) => setNewQuestion({ ...newQuestion, option_a: e.target.value })}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="option_b">Option B</Label>
                          <Input
                            id="option_b"
                            value={newQuestion.option_b}
                            onChange={(e) => setNewQuestion({ ...newQuestion, option_b: e.target.value })}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="option_c">Option C</Label>
                          <Input
                            id="option_c"
                            value={newQuestion.option_c}
                            onChange={(e) => setNewQuestion({ ...newQuestion, option_c: e.target.value })}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="option_d">Option D</Label>
                          <Input
                            id="option_d"
                            value={newQuestion.option_d}
                            onChange={(e) => setNewQuestion({ ...newQuestion, option_d: e.target.value })}
                            required
                          />
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="correct">Correct Option</Label>
                        <Select 
                          id="correct"
                          value={newQuestion.correct_option} 
                          onChange={(e) => setNewQuestion({ ...newQuestion, correct_option: e.target.value })}
                        >
                          <option value="a">Option A</option>
                          <option value="b">Option B</option>
                          <option value="c">Option C</option>
                          <option value="d">Option D</option>
                        </Select>
                      </div>
                      <Button type="submit" className="w-full">Add Question</Button>
                    </form>
                  </DialogContent>
                </Dialog>

              <div className="grid gap-4">
                {questions.map((question, index) => (
                  <Card key={question.id} className="p-6">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-semibold">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-medium mb-3">{question.question_text}</p>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className={`p-2 rounded ${question.correct_option === "a" ? "bg-green-500/20 text-green-400" : "bg-white/5 text-gray-400"}`}>
                            A: {question.option_a}
                          </div>
                          <div className={`p-2 rounded ${question.correct_option === "b" ? "bg-green-500/20 text-green-400" : "bg-white/5 text-gray-400"}`}>
                            B: {question.option_b}
                          </div>
                          <div className={`p-2 rounded ${question.correct_option === "c" ? "bg-green-500/20 text-green-400" : "bg-white/5 text-gray-400"}`}>
                            C: {question.option_c}
                          </div>
                          <div className={`p-2 rounded ${question.correct_option === "d" ? "bg-green-500/20 text-green-400" : "bg-white/5 text-gray-400"}`}>
                            D: {question.option_d}
                          </div>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
                {questions.length === 0 && (
                  <Card className="p-12 text-center">
                    <p className="text-gray-400">No questions added yet. Click "Add Question" to get started.</p>
                  </Card>
                )}
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>
    </AppShell>
  );
}

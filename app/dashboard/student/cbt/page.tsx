"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Play, Clock, CheckCircle, History } from "lucide-react";

interface CBTExam {
  id: number;
  title: string;
  class: string;
  duration_minutes: number;
  status: string;
}

interface CBTQuestion {
  id: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
}

interface CBTResult {
  id: number;
  exam_id: number;
  score: number;
  total_questions: number;
  date_taken: string;
}

export default function StudentCBTPage() {
  const [exams, setExams] = useState<CBTExam[]>([]);
  const [history, setHistory] = useState<CBTResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedExam, setSelectedExam] = useState<CBTExam | null>(null);
  const [questions, setQuestions] = useState<CBTQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [showExam, setShowExam] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [examSubmitted, setExamSubmitted] = useState(false);
  const [examResult, setExamResult] = useState<CBTResult | null>(null);
  const [activeTab, setActiveTab] = useState("available");

  const fetchExams = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/cbt/exams/active", {
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

  const fetchHistory = async () => {
    try {
      const response = await fetch("/api/cbt/results/history", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (error) {
      console.error("Failed to fetch history:", error);
    }
  };

  const startExam = async (exam: CBTExam) => {
    try {
      const response = await fetch(`/api/cbt/exams/${exam.id}/questions`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setQuestions(data);
        setSelectedExam(exam);
        setAnswers({});
        setTimeRemaining(exam.duration_minutes * 60);
        setShowExam(true);
        setExamSubmitted(false);
        setExamResult(null);
      }
    } catch (error) {
      console.error("Failed to fetch questions:", error);
    }
  };

  const submitExam = async () => {
    try {
      const response = await fetch("/api/cbt/results", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          exam_id: selectedExam?.id,
          answers: answers
        })
      });
      if (response.ok) {
        const data = await response.json();
        setExamResult(data);
        setExamSubmitted(true);
        fetchHistory();
      }
    } catch (error) {
      console.error("Failed to submit exam:", error);
    }
  };

  useState(() => {
    fetchExams();
    fetchHistory();
  });

  // Timer effect
  useState(() => {
    let interval: NodeJS.Timeout;
    if (showExam && !examSubmitted && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            submitExam();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  });

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <AppShell
      eyebrow="Student Dashboard"
      title="Computer Based Tests"
      description="Take exams and view your CBT history"
    >
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="available">Available Exams</TabsTrigger>
          <TabsTrigger value="history">Exam History</TabsTrigger>
        </TabsList>

        <TabsContent value="available" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-semibold text-white">Available Exams</h3>
            <Badge tone="neutral">{exams.length} exams available</Badge>
          </div>

          {isLoading ? (
            <Card className="p-6">
              <p className="text-center text-gray-400">Loading exams...</p>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {exams.map((exam) => (
                <Card key={exam.id} className="p-6">
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-2">{exam.title}</h4>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <Clock className="w-4 h-4" />
                        <span>{exam.duration_minutes} minutes</span>
                      </div>
                    </div>
                    <Button 
                      className="w-full" 
                      onClick={() => startExam(exam)}
                    >
                      <Play className="w-4 h-4 mr-2" />
                      Start Exam
                    </Button>
                  </div>
                </Card>
              ))}
              {exams.length === 0 && (
                <Card className="p-12 col-span-full text-center">
                  <p className="text-gray-400">No active exams available at the moment.</p>
                </Card>
              )}
            </div>
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-semibold text-white">Exam History</h3>
            <Badge tone="neutral">{history.length} completed</Badge>
          </div>

          <div className="grid gap-4">
            {history.map((result) => (
              <Card key={result.id} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center">
                      <CheckCircle className="w-6 h-6" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Exam #{result.exam_id}</p>
                      <p className="text-sm text-gray-400">
                        Score: {result.score}/{result.total_questions} ({Math.round((result.score / result.total_questions) * 100)}%)
                      </p>
                      <p className="text-xs text-gray-500">
                        Completed: {new Date(result.date_taken).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <Badge tone={result.score / result.total_questions >= 0.5 ? "good" : "warn"}>
                    {result.score}/{result.total_questions}
                  </Badge>
                </div>
              </Card>
            ))}
            {history.length === 0 && (
              <Card className="p-12 text-center">
                <p className="text-gray-400">No exam history yet. Take your first exam to see results here.</p>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Exam Dialog */}
      <Dialog open={showExam} onOpenChange={setShowExam}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between">
              <span>{selectedExam?.title}</span>
              <Badge tone="neutral">
                <Clock className="w-4 h-4 mr-1" />
                {formatTime(timeRemaining)}
              </Badge>
            </DialogTitle>
          </DialogHeader>

          {examSubmitted && examResult ? (
            <div className="text-center py-12">
              <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center">
                <CheckCircle className="w-10 h-10" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">Exam Submitted!</h3>
              <p className="text-gray-400 mb-4">Your results have been recorded.</p>
              <div className="text-4xl font-bold text-[#f9d28a] mb-6">
                {examResult.score}/{examResult.total_questions}
              </div>
              <p className="text-sm text-gray-400">
                Percentage: {Math.round((examResult.score / examResult.total_questions) * 100)}%
              </p>
              <Button className="mt-6" onClick={() => setShowExam(false)}>
                Close
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {questions.map((question, index) => (
                <Card key={question.id} className="p-6">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-semibold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="text-white font-medium mb-4">{question.question_text}</p>
                      <div className="space-y-3">
                        <div className="flex items-center space-x-2">
                          <input
                            type="radio"
                            id={`q${question.id}-a`}
                            name={`q${question.id}`}
                            value="a"
                            checked={answers[question.id] === "a"}
                            onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })}
                            className="w-4 h-4"
                          />
                          <Label htmlFor={`q${question.id}-a`} className="cursor-pointer">
                            A: {question.option_a}
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <input
                            type="radio"
                            id={`q${question.id}-b`}
                            name={`q${question.id}`}
                            value="b"
                            checked={answers[question.id] === "b"}
                            onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })}
                            className="w-4 h-4"
                          />
                          <Label htmlFor={`q${question.id}-b`} className="cursor-pointer">
                            B: {question.option_b}
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <input
                            type="radio"
                            id={`q${question.id}-c`}
                            name={`q${question.id}`}
                            value="c"
                            checked={answers[question.id] === "c"}
                            onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })}
                            className="w-4 h-4"
                          />
                          <Label htmlFor={`q${question.id}-c`} className="cursor-pointer">
                            C: {question.option_c}
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <input
                            type="radio"
                            id={`q${question.id}-d`}
                            name={`q${question.id}`}
                            value="d"
                            checked={answers[question.id] === "d"}
                            onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })}
                            className="w-4 h-4"
                          />
                          <Label htmlFor={`q${question.id}-d`} className="cursor-pointer">
                            D: {question.option_d}
                          </Label>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
              <div className="flex justify-end gap-4">
                <Button variant="outline" onClick={() => setShowExam(false)}>
                  Cancel
                </Button>
                <Button onClick={submitExam} disabled={Object.keys(answers).length < questions.length}>
                  Submit Exam ({Object.keys(answers).length}/{questions.length} answered)
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}

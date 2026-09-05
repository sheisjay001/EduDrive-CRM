"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Lock, CheckCircle, AlertCircle } from "lucide-react";

interface Result {
  id: number;
  subject: string;
  ca_score: number;
  exam_score: number;
  total_score: number;
  grade: string;
  term: string;
  session: string;
}

export default function StudentResultsPage() {
  const [results, setResults] = useState<Result[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showVerify, setShowVerify] = useState(false);
  const [pinCode, setPinCode] = useState("");
  const [serialNumber, setSerialNumber] = useState("");
  const [error, setError] = useState("");
  const [verified, setVerified] = useState(false);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/results/check", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          pin_code: pinCode,
          serial_number: serialNumber
        })
      });

      const data = await response.json();

      if (response.ok) {
        setResults(data);
        setVerified(true);
        setShowVerify(false);
      } else {
        setError(data.detail || "Invalid PIN or serial number");
      }
    } catch (error) {
      setError("Failed to verify PIN. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade.toUpperCase()) {
      case "A":
      case "A1":
        return "text-green-400";
      case "B":
      case "B2":
      case "B3":
        return "text-blue-400";
      case "C":
      case "C4":
      case "C5":
      case "C6":
        return "text-yellow-400";
      default:
        return "text-red-400";
    }
  };

  return (
    <AppShell
      eyebrow="Student Dashboard"
      title="My Results"
      description="Check your academic results using your scratch card PIN"
    >
      {!verified ? (
        <div className="max-w-md mx-auto mt-12">
          <Card className="p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center">
              <Lock className="w-8 h-8" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Results Protected</h3>
            <p className="text-gray-400 mb-6">
              Enter your scratch card PIN and serial number to view your results
            </p>
            <Button onClick={() => setShowVerify(true)} className="w-full">
              <Lock className="w-4 h-4 mr-2" />
              Verify PIN
            </Button>
          </Card>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xl font-semibold text-white">Academic Results</h3>
              <p className="text-sm text-gray-400">{results.length} subjects</p>
            </div>
            <Button variant="outline" onClick={() => setVerified(false)}>
              Verify Different PIN
            </Button>
          </div>

          <div className="grid gap-4">
            {results.map((result) => (
              <Card key={result.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h4 className="text-lg font-semibold text-white">{result.subject}</h4>
                      <Badge tone="neutral">{result.term} • {result.session}</Badge>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-400">CA Score</p>
                        <p className="text-white font-medium">{result.ca_score}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Exam Score</p>
                        <p className="text-white font-medium">{result.exam_score}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Total</p>
                        <p className="text-white font-medium">{result.total_score}</p>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-3xl font-bold ${getGradeColor(result.grade)}`}>
                      {result.grade}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Grade</p>
                  </div>
                </div>
              </Card>
            ))}
            {results.length === 0 && (
              <Card className="p-12 text-center">
                <AlertCircle className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                <p className="text-gray-400">No results found for your account.</p>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* PIN Verification Dialog */}
      <Dialog open={showVerify} onOpenChange={setShowVerify}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Verify Scratch Card PIN</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleVerify} className="space-y-4">
            <div>
              <Label htmlFor="pin">PIN Code</Label>
              <Input
                id="pin"
                type="text"
                placeholder="Enter 12-digit PIN"
                value={pinCode}
                onChange={(e) => setPinCode(e.target.value)}
                required
                maxLength={12}
              />
            </div>
            <div>
              <Label htmlFor="serial">Serial Number</Label>
              <Input
                id="serial"
                type="text"
                placeholder="Enter serial number"
                value={serialNumber}
                onChange={(e) => setSerialNumber(e.target.value)}
                required
              />
            </div>
            {error && (
              <div className="flex items-center gap-2 text-red-400 text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
              </div>
            )}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Verifying..." : "Verify & View Results"}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}

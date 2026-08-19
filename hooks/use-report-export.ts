import { useState } from "react";

type ExportFormat = "pdf" | "excel" | "csv";

interface ReportData {
  title: string;
  data: Record<string, unknown>[];
  columns: string[];
  metadata?: Record<string, unknown>;
}

export function useReportExport() {
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const exportToCSV = (data: ReportData) => {
    const headers = data.columns.join(",");
    const rows = data.data.map(row => 
      data.columns.map(col => {
        const value = row[col];
        // Handle values that contain commas or quotes
        const stringValue = String(value ?? "");
        if (stringValue.includes(",") || stringValue.includes('"')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(",")
    );
    
    const csvContent = [headers, ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    
    link.setAttribute("href", url);
    link.setAttribute("download", `${data.title.replace(/\s+/g, "_")}.csv`);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportToExcel = async (data: ReportData) => {
    // In a real implementation, you would use a library like xlsx or exceljs
    // For now, we'll create a simple CSV with .xlsx extension as a placeholder
    const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";
    
    try {
      const response = await fetch(`${API_URL}/reports/export/excel`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Failed to export to Excel");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${data.title.replace(/\s+/g, "_")}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch {
      // Fallback to CSV if API call fails
      exportToCSV(data);
    }
  };

  const exportToPDF = async (data: ReportData) => {
    // In a real implementation, you would use a library like jsPDF or react-pdf
    const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";
    
    try {
      const response = await fetch(`${API_URL}/reports/export/pdf`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Failed to export to PDF");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${data.title.replace(/\s+/g, "_")}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch {
      setError("PDF export requires server-side generation. Please try again later.");
    }
  };

  const exportReport = async (data: ReportData, format: ExportFormat) => {
    setIsExporting(true);
    setExportProgress(0);
    setError(null);

    try {
      setExportProgress(25);

      switch (format) {
        case "csv":
          exportToCSV(data);
          break;
        case "excel":
          await exportToExcel(data);
          break;
        case "pdf":
          await exportToPDF(data);
          break;
        default:
          throw new Error("Unsupported export format");
      }

      setExportProgress(100);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Export failed");
    } finally {
      setIsExporting(false);
    }
  };

  const scheduleReport = async (data: ReportData, format: ExportFormat, schedule: {
    frequency: "daily" | "weekly" | "monthly";
    email: string;
  }) => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";
    
    try {
      const response = await fetch(`${API_URL}/reports/schedule`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          ...data,
          format,
          schedule,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to schedule report");
      }

      return await response.json();
    } catch {
      throw new Error("Failed to schedule report");
    }
  };

  return {
    isExporting,
    exportProgress,
    error,
    exportReport,
    scheduleReport,
  };
}

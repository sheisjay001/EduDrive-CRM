import { useState, useCallback } from "react";
import { getAccessToken } from "@/services/auth-storage";

interface FileUploadOptions {
  maxSize?: number; // in bytes
  allowedTypes?: string[];
  maxFiles?: number;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  uploadedAt: Date;
}

export function useFileUpload(options: FileUploadOptions = {}) {
  const {
    maxSize = 10 * 1024 * 1024, // 10MB default
    allowedTypes = [],
    maxFiles = 10,
  } = options;

  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    if (maxSize && file.size > maxSize) {
      return `File size exceeds maximum of ${maxSize / 1024 / 1024}MB`;
    }

    if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
      return `File type ${file.type} is not allowed`;
    }

    return null;
  };

  const uploadFile = useCallback(async (file: File): Promise<UploadedFile> => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("entity_type", "document");
    formData.append("entity_id", "temp");

    try {
      const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();
      
      return {
        id: data.id || Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        type: file.type,
        url: data.url || URL.createObjectURL(file),
        uploadedAt: new Date(),
      };
    } catch {
      throw new Error("Failed to upload file");
    }
  }, [validateFile]);

  const handleFileSelect = useCallback(async (selectedFiles: FileList | null) => {
    if (!selectedFiles) return;

    setError(null);

    if (files.length + selectedFiles.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`);
      return;
    }

    const validFiles: File[] = [];
    const validationErrors: string[] = [];

    Array.from(selectedFiles).forEach(file => {
      const error = validateFile(file);
      if (error) {
        validationErrors.push(`${file.name}: ${error}`);
      } else {
        validFiles.push(file);
      }
    });

    if (validationErrors.length > 0) {
      setError(validationErrors.join(", "));
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const uploadedFiles: UploadedFile[] = [];
      
      for (let i = 0; i < validFiles.length; i++) {
        const file = validFiles[i];
        const uploaded = await uploadFile(file);
        uploadedFiles.push(uploaded);
        setUploadProgress(((i + 1) / validFiles.length) * 100);
      }

      setFiles(prev => [...prev, ...uploadedFiles]);
    } catch {
      setError("Failed to upload one or more files");
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [files.length, maxFiles, uploadFile]);

  const removeFile = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  }, []);

  const clearAll = useCallback(() => {
    setFiles([]);
    setError(null);
  }, []);

  return {
    files,
    isUploading,
    uploadProgress,
    error,
    handleFileSelect,
    removeFile,
    clearAll,
  };
}

import { create } from "zustand";

type UploadStatus = "idle" | "uploading" | "processing" | "done" | "error";

interface ReceiptStore {
  uploadStatus: UploadStatus;
  uploadProgress: number;
  ocrStage: string;
  error: string | null;
  setUploadStatus: (status: UploadStatus) => void;
  setUploadProgress: (progress: number) => void;
  setOcrStage: (stage: string) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useReceiptStore = create<ReceiptStore>((set) => ({
  uploadStatus: "idle",
  uploadProgress: 0,
  ocrStage: "",
  error: null,
  setUploadStatus: (status) => set({ uploadStatus: status }),
  setUploadProgress: (progress) => set({ uploadProgress: progress }),
  setOcrStage: (stage) => set({ ocrStage: stage }),
  setError: (error) => set({ error }),
  reset: () => set({ uploadStatus: "idle", uploadProgress: 0, ocrStage: "", error: null }),
}));

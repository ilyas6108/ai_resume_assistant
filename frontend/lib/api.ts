const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export type UploadResult = {
  data: {
    filename: string;
    extension: string;
    chunks: number;
    collection_count: number;
  } | [];
  message: string;
  error: string;
};

export type AskResult = {
  data: { content: string } | [];
  message: string;
  error: string;
};

export const FEATURES = [
  { value: "ats_score", label: "ATS score" },
  { value: "skill_gap", label: "Skill gap" },
  { value: "job_match", label: "Job match" },
  { value: "interview_questions", label: "Interview questions" },
  { value: "resume_rewrite", label: "Resume rewrite" },
] as const;

export async function uploadDocument(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_URL}/upload-document`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function askQuery(query: string, feature: string): Promise<AskResult> {
  const res = await fetch(`${API_URL}/ask-query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, feature }),
  });
  return res.json();
}

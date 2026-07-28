"use client";

import { useRef, useState } from "react";
import { uploadDocument, askQuery, FEATURES } from "@/lib/api";

type UploadedDoc = {
  filename: string;
  extension: string;
  chunks: number;
  collection_count: number;
};

const ALLOWED_EXT = [".pdf", ".docx"];

// The backend uses this text both as the vector-search query and as the
// {job_description} / {target_role} value in the prompt — so even features
// that don't strictly need a job description (ats_score) need something here
// for retrieval to work well. Users can edit or replace this freely.
const DEFAULT_QUERY: Record<string, string> = {
  ats_score: "Evaluate this resume for ATS compatibility.",
  skill_gap: "",
  job_match: "",
  interview_questions: "Generate interview questions based on this resume.",
  resume_rewrite: "",
};

export default function Home() {
  // -- upload state --
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [doc, setDoc] = useState<UploadedDoc | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // -- ask state --
  const [query, setQuery] = useState(DEFAULT_QUERY[FEATURES[0].value]);
  const [feature, setFeature] = useState<string>(FEATURES[0].value);
  const [isAsking, setIsAsking] = useState(false);
  const [askError, setAskError] = useState("");
  const [answer, setAnswer] = useState("");

  async function handleFile(file: File) {
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_EXT.includes(ext)) {
      setUploadError(`Can't use a ${ext} file. Upload a .pdf or .docx instead.`);
      return;
    }

    setUploadError("");
    setIsUploading(true);
    setDoc(null);

    try {
      const result = await uploadDocument(file);
      if (result.error) {
        setUploadError(result.error);
      } else {
        setDoc(result.data as UploadedDoc);
      }
    } catch {
      setUploadError("Couldn't reach the server. Confirm the API is running on port 8000.");
    } finally {
      setIsUploading(false);
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }

  function resetUpload() {
    setDoc(null);
    setAnswer("");
    setQuery("");
    setUploadError("");
    setAskError("");
  }

  async function handleAsk() {
    if (!query.trim()) return;

    setIsAsking(true);
    setAskError("");
    setAnswer("");

    try {
      const result = await askQuery(query, feature);
      if (result.error) {
        setAskError(result.error);
      } else {
        setAnswer((result.data as { content: string }).content);
      }
    } catch {
      setAskError("Couldn't reach the server. Confirm the API is running on port 8000.");
    } finally {
      setIsAsking(false);
    }
  }

  function handleFeatureChange(next: string) {
    const wasDefault = query === DEFAULT_QUERY[feature];
    setFeature(next);
    if (wasDefault || !query.trim()) {
      setQuery(DEFAULT_QUERY[next] ?? "");
    }
  }

  const selectedFeature = FEATURES.find((f) => f.value === feature);

  return (
    <main className="page">
      <div className="column">
        <div className="header">
          <p className="eyebrow">Resume assistant</p>
          <h1 className="title">Get a straight read on your resume</h1>
          <p className="subtitle">
            Upload your resume once, then ask for as many kinds of feedback as you want —
            ATS scoring, skill gaps against a job description, interview prep, and more.
          </p>
        </div>

        <div className="steps">
          <div className={`step ${doc ? "is-done" : "is-active"}`}>
            <span className="step-dot">{doc ? "✓" : "1"}</span>
            Upload
          </div>
          <div className="step-rule" />
          <div className={`step ${doc ? "is-active" : ""}`}>
            <span className="step-dot">2</span>
            Analyze
          </div>
        </div>

        {/* -------- Step 1: upload -------- */}
        {!doc && (
          <div className="card">
            <p className="card-label">Upload resume</p>
            <label
              className={`dropzone ${isDragging ? "is-drag" : ""}`}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={onDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              />
              <div className="dropzone-icon">{isUploading && <div className="scan-line" />}</div>
              <p className="dropzone-text">
                {isUploading ? "Scanning resume…" : "Drop your resume here, or click to choose a file"}
              </p>
              <p className="dropzone-hint">PDF or DOCX</p>
            </label>
            {uploadError && <div className="alert alert-error">{uploadError}</div>}
          </div>
        )}

        {/* -------- Upload confirmation -------- */}
        {doc && (
          <div className="card">
            <p className="card-label">Resume on file</p>
            <div className="stamp-row">
              <span className="stamp">Scanned ✓</span>
              <span className="file-meta">
                {doc.filename} <span>· {doc.chunks} chunks indexed</span>
              </span>
            </div>
            <div style={{ marginTop: 16 }}>
              <button className="btn btn-ghost" onClick={resetUpload}>
                Upload a different resume
              </button>
            </div>
          </div>
        )}

        {/* -------- Step 2: ask -------- */}
        {doc && (
          <div className="card">
            <p className="card-label">Ask about this resume</p>

            <div className="field">
              <label className="field-label">What do you want to know?</label>
              <select className="select" value={feature} onChange={(e) => handleFeatureChange(e.target.value)}>
                {FEATURES.map((f) => (
                  <option key={f.value} value={f.value}>
                    {f.label}
                  </option>
                ))}
              </select>
              <p className="feature-hint">{featureHint(feature)}</p>
            </div>

            <div className="field">
              <label className="field-label">
                {feature === "ats_score" ? "Anything specific to check for (optional)" : "Job description or question"}
              </label>
              <textarea
                className="textarea"
                placeholder={placeholderFor(feature)}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </div>

            <button className="btn btn-primary" onClick={handleAsk} disabled={isAsking || !query.trim()}>
              {isAsking && <span className="spinner" />}
              {isAsking ? "Analyzing…" : `Run ${selectedFeature?.label.toLowerCase()}`}
            </button>

            {askError && <div className="alert alert-error">{askError}</div>}
          </div>
        )}

        {/* -------- Answer -------- */}
        {answer && (
          <div className="card">
            <p className="card-label">Result</p>
            <div className="result">{answer}</div>
          </div>
        )}
      </div>
    </main>
  );
}

function featureHint(feature: string): string {
  switch (feature) {
    case "ats_score":
      return "Scores formatting, keyword clarity, and machine-readability.";
    case "skill_gap":
      return "Compares your resume against a job description you paste in.";
    case "job_match":
      return "Rates overall fit against a job description, not just keywords.";
    case "interview_questions":
      return "Generates questions tailored to what's actually in your resume.";
    case "resume_rewrite":
      return "Rewrites a section to be more concise and quantified.";
    default:
      return "";
  }
}

function placeholderFor(feature: string): string {
  switch (feature) {
    case "ats_score":
      return "e.g. Pay extra attention to the skills section";
    case "resume_rewrite":
      return "e.g. Target role: Senior Backend Engineer";
    default:
      return "Paste the job description here…";
  }
}

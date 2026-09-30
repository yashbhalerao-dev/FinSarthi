"use client";

import { ChangeEvent, useEffect, useState } from "react";
import { Banner } from "@/components/Banner";
import { StatusBadge } from "@/components/StatusBadge";
import {
  ApiError,
  getProfile,
  listDocuments,
  processDocument,
  updateProfile,
  uploadDocument,
} from "@/lib/api";
import { DEMO_CASES, jsonFile } from "@/lib/demo";
import { getStoredProfileId } from "@/lib/session";
import type { ApplicantProfile, DocumentRecord } from "@/types/api";

export default function DocumentsPage() {
  const [hasProfile, setHasProfile] = useState(false);
  const [profile, setProfile] = useState<ApplicantProfile | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [selected, setSelected] = useState<DocumentRecord | null>(null);
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function refresh(profileId: string) {
    const [nextProfile, docs] = await Promise.all([getProfile(profileId), listDocuments(profileId)]);
    setProfile(nextProfile);
    setDocuments(docs);
    setSelected((current) => docs.find((item) => item.id === current?.id) ?? docs[0] ?? null);
  }

  useEffect(() => {
    const id = getStoredProfileId();
    setHasProfile(Boolean(id));
    if (!id) {
      setLoading(false);
      return;
    }
    refresh(id)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load documents."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selected) {
      setEdits({});
      return;
    }
    const next: Record<string, string> = {};
    for (const [key, value] of Object.entries(selected.extracted_fields ?? {})) {
      next[key] = value == null ? "" : String(value);
    }
    setEdits(next);
  }, [selected]);

  async function onUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    const profileId = getStoredProfileId();
    if (!file || !profileId) return;
    setBusy(true);
    setError(null);
    setSuccess(null);
    try {
      const uploaded = await uploadDocument(profileId, file);
      setSuccess(`Uploaded ${uploaded.filename}. Processing…`);
      await processDocument(uploaded.id);
      await refresh(profileId);
      setSuccess(`Processed ${uploaded.filename}.`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed.");
    } finally {
      setBusy(false);
      event.target.value = "";
    }
  }

  async function attachDemoFile() {
    const profileId = getStoredProfileId();
    if (!profileId) return;
    const demo = DEMO_CASES.find((item) => item.id === profileId) ?? DEMO_CASES[0];
    const file = demo.files[0];
    setBusy(true);
    setError(null);
    try {
      const uploaded = await uploadDocument(profileId, jsonFile(file.filename, file.body));
      await processDocument(uploaded.id);
      await refresh(profileId);
      setSuccess(`Attached synthetic file ${file.filename} and processed it.`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Demo upload failed.");
    } finally {
      setBusy(false);
    }
  }

  async function processAgain() {
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      await processDocument(selected.id);
      const profileId = getStoredProfileId();
      if (profileId) await refresh(profileId);
      setSuccess("Document reprocessed.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Processing failed.");
    } finally {
      setBusy(false);
    }
  }

  async function saveCorrections() {
    if (!profile) return;
    setBusy(true);
    setError(null);
    try {
      const numeric = new Set(["age", "income", "turnover", "investment"]);
      const next = { ...profile };
      const uncertain = new Set(profile.uncertain_fields ?? []);
      for (const [key, raw] of Object.entries(edits)) {
        const value = numeric.has(key) ? (raw === "" ? null : Number(raw)) : raw || null;
        if (key in next) {
          (next as unknown as Record<string, unknown>)[key] = value;
        }
        if (raw !== "") uncertain.delete(key);
      }
      const saved = await updateProfile(profile.id, {
        applicant_type: next.applicant_type,
        age: next.age,
        state: next.state,
        district: next.district,
        income: next.income,
        occupation: next.occupation,
        category: next.category,
        business_type: next.business_type,
        registration_status: next.registration_status,
        turnover: next.turnover,
        investment: next.investment,
        uncertain_fields: [...uncertain],
        source_evidence: next.source_evidence,
      });
      setProfile(saved);
      setSuccess("Corrections saved to the applicant profile.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed.");
    } finally {
      setBusy(false);
    }
  }

  const uncertain = new Set(selected?.uncertain_fields ?? profile?.uncertain_fields ?? []);

  return (
    <main className="shell">
      <p className="eyebrow">Evidence</p>
      <h1>Documents</h1>
      {loading ? <p className="muted">Loading…</p> : null}
      {error ? <Banner tone="bad">{error}</Banner> : null}
      {success ? <Banner tone="ok">{success}</Banner> : null}
      {!hasProfile && !loading ? (
        <Banner tone="warn">Create or load a profile before uploading documents.</Banner>
      ) : null}

      <div className="actions">
        <label className="button">
          Upload file
          <input type="file" hidden onChange={onUpload} disabled={busy || !profile} />
        </label>
        <button className="button secondary" disabled={busy || !profile} onClick={() => void attachDemoFile()}>
          Attach synthetic demo JSON
        </button>
        <button className="button secondary" disabled={busy || !selected} onClick={() => void processAgain()}>
          {busy ? "Working…" : "Reprocess selected"}
        </button>
      </div>

      {documents.length === 0 && !loading ? (
        <section className="card">
          <h2>No documents</h2>
          <p>Upload a PDF/image later, or attach a synthetic JSON demo file now.</p>
        </section>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>File</th>
              <th>Type</th>
              <th>Status</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id} onClick={() => setSelected(doc)} style={{ cursor: "pointer" }}>
                <td>{doc.filename}</td>
                <td>{doc.document_type}</td>
                <td>
                  <StatusBadge status={doc.extraction_status} />
                </td>
                <td>{Math.round(doc.confidence * 100)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selected ? (
        <section className="card" style={{ marginTop: "1.2rem" }}>
          <h2>Extracted fields</h2>
          <p className="small">
            Uncertain fields are highlighted. Saving writes corrections to the profile via PUT
            /api/profile.
          </p>
          <div className="form-grid">
            {Object.keys(edits).length === 0 ? (
              <p className="muted">No extracted fields on this document.</p>
            ) : (
              Object.entries(edits).map(([key, value]) => (
                <label key={key}>
                  {key}
                  <input
                    className={uncertain.has(key) ? "uncertain" : undefined}
                    value={value}
                    onChange={(e) => setEdits((current) => ({ ...current, [key]: e.target.value }))}
                  />
                </label>
              ))
            )}
          </div>
          <div className="actions">
            <button className="button" disabled={busy} onClick={() => void saveCorrections()}>
              Save corrections
            </button>
          </div>
        </section>
      ) : null}
    </main>
  );
}

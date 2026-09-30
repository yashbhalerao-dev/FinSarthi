"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Banner } from "@/components/Banner";
import { StatusBadge } from "@/components/StatusBadge";
import {
  ApiError,
  createProfile,
  evaluateEligibility,
  getHealth,
  getProfile,
  getResult,
  listDocuments,
  processDocument,
  searchPolicies,
  updateProfile,
  uploadDocument,
} from "@/lib/api";
import { DEMO_CASES, jsonFile } from "@/lib/demo";
import {
  getStoredProfileId,
  getStoredResultId,
  setStoredProfileId,
  setStoredResultId,
} from "@/lib/session";
import type { ApplicantProfile, DocumentRecord, EligibilityResult } from "@/types/api";

export default function DashboardPage() {
  const [backend, setBackend] = useState<"checking" | "ok" | "down">("checking");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [profile, setProfile] = useState<ApplicantProfile | null>(null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [policyCount, setPolicyCount] = useState<number | null>(null);
  const [result, setResult] = useState<EligibilityResult | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await getHealth();
      setBackend("ok");
    } catch {
      setBackend("down");
      setLoading(false);
      return;
    }
    const profileId = getStoredProfileId();
    if (!profileId) {
      setProfile(null);
      setDocuments([]);
      setPolicyCount(null);
      setResult(null);
      setLoading(false);
      return;
    }
    try {
      const nextProfile = await getProfile(profileId);
      setProfile(nextProfile);
      const docs = await listDocuments(profileId);
      setDocuments(docs);
      try {
        const discovered = await searchPolicies(profileId);
        setPolicyCount(discovered.policies.length);
      } catch {
        setPolicyCount(null);
      }
      const resultId = getStoredResultId();
      if (resultId) {
        try {
          setResult(await getResult(resultId));
        } catch {
          setResult(null);
        }
      } else {
        setResult(null);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load dashboard.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function loadDemo(id: (typeof DEMO_CASES)[number]["id"]) {
    const demo = DEMO_CASES.find((item) => item.id === id);
    if (!demo) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await getHealth();
      let next: ApplicantProfile;
      try {
        next = await getProfile(demo.id);
        next = await updateProfile(demo.id, { ...demo.profile, id: undefined });
      } catch {
        next = await createProfile(demo.profile);
      }
      const existing = await listDocuments(next.id);
      if (existing.length === 0) {
        for (const file of demo.files) {
          const uploaded = await uploadDocument(next.id, jsonFile(file.filename, file.body));
          await processDocument(uploaded.id);
        }
      }
      const evaluated = await evaluateEligibility(next.id);
      const stored = await getResult(evaluated.id);
      setStoredProfileId(next.id);
      setStoredResultId(stored.id);
      setNotice(`${demo.label} loaded from the FastAPI backend.`);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Demo load failed. Is the API running?");
    } finally {
      setBusy(false);
    }
  }

  const headline = result?.policies[0]?.overall_status;

  return (
    <main className="shell">
      <p className="eyebrow">Workspace</p>
      <h1>Dashboard</h1>
      {backend === "checking" ? <Banner tone="info">Checking FastAPI…</Banner> : null}
      {backend === "down" ? (
        <Banner tone="bad">
          Backend is not reachable at the API base URL. Start FastAPI on port 8000.
        </Banner>
      ) : null}
      {error ? <Banner tone="bad">{error}</Banner> : null}
      {notice ? <Banner tone="ok">{notice}</Banner> : null}
      {loading ? <p className="muted">Loading…</p> : null}

      <div className="actions">
        {DEMO_CASES.map((demo) => (
          <button
            key={demo.id}
            className="button secondary"
            disabled={busy || backend !== "ok"}
            onClick={() => void loadDemo(demo.id)}
          >
            {demo.label}
          </button>
        ))}
      </div>
      <p className="muted small">
        Demo controls call the live profile, document, evaluate, and result APIs. They do not
        decide eligibility in the browser.
      </p>

      {!loading && !profile ? (
        <section className="card">
          <h2>No profile yet</h2>
          <p>Create a profile or load a synthetic demo case to begin.</p>
          <div className="actions">
            <Link className="button" href="/profile">
              Create profile
            </Link>
          </div>
        </section>
      ) : null}

      {profile ? (
        <div className="grid">
          <section className="card">
            <h2>Profile</h2>
            <p>
              {profile.applicant_type.replace("_", " ")} · {profile.state ?? "No state"} ·{" "}
              {profile.occupation ?? "No occupation"}
            </p>
            <p className="small">ID {profile.id}</p>
            <Link className="button secondary" href="/profile">
              Edit profile
            </Link>
          </section>
          <section className="card">
            <h2>Documents</h2>
            <p>
              {documents.length === 0
                ? "No documents uploaded."
                : `${documents.length} file(s), ${documents.filter((d) => d.extraction_status === "processed").length} processed.`}
            </p>
            <Link className="button secondary" href="/documents">
              Manage documents
            </Link>
          </section>
          <section className="card">
            <h2>Discovery</h2>
            <p>
              {policyCount === null
                ? "Run discovery after a profile exists."
                : `${policyCount} matching synthetic demo polic${policyCount === 1 ? "y" : "ies"}.`}
            </p>
            <Link className="button secondary" href="/discovery">
              Open discovery
            </Link>
          </section>
          <section className="card">
            <h2>Eligibility</h2>
            <p>{headline ? <StatusBadge status={headline} /> : "Not evaluated yet."}</p>
            <Link className="button secondary" href="/results">
              View results
            </Link>
          </section>
        </div>
      ) : null}
    </main>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import { Banner } from "@/components/Banner";
import { StatusBadge } from "@/components/StatusBadge";
import { ApiError, evaluateEligibility, getResult } from "@/lib/api";
import { getStoredProfileId, getStoredResultId, setStoredResultId } from "@/lib/session";
import type { EligibilityResult, PolicyEvaluation } from "@/types/api";

function PolicyResult({ item }: { item: PolicyEvaluation }) {
  return (
    <article className="card">
      {item.synthetic ? <p className="eyebrow">Synthetic demo policy</p> : null}
      {item.review_required ? <Banner tone="warn">Review required</Banner> : null}
      <h2>{item.policy_name}</h2>
      <StatusBadge status={item.overall_status} />
      <p>{item.explanation}</p>

      <h3>Conditions</h3>
      <table className="table">
        <thead>
          <tr>
            <th>Field</th>
            <th>Rule</th>
            <th>Actual</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {item.conditions.map((condition) => (
            <tr key={`${item.policy_id}-${condition.field}`}>
              <td>{condition.field}</td>
              <td>
                {condition.operator} {String(condition.expected)}
              </td>
              <td>{condition.actual == null ? "—" : String(condition.actual)}</td>
              <td>
                <StatusBadge status={condition.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {item.conditions[0]?.reason ? (
        <p className="small muted">{item.conditions.map((c) => c.reason).filter(Boolean).join(" ")}</p>
      ) : null}

      <h3>Benefit</h3>
      {item.benefit.supported_by_source && item.benefit.amount != null ? (
        <p>
          {item.benefit.amount} {item.benefit.currency ?? ""} · {item.benefit.basis}
        </p>
      ) : (
        <p className="muted">No source-backed benefit amount. Nothing was invented.</p>
      )}

      <h3>Documents</h3>
      <p className="small">Required: {item.required_documents.join(", ") || "none"}</p>
      <p className="small">
        Missing: {item.missing_documents.length ? item.missing_documents.join(", ") : "none"}
      </p>

      <h3>Evidence</h3>
      {item.evidence.length === 0 ? (
        <p className="muted">No evidence chunks on this result.</p>
      ) : (
        item.evidence.map((ev) => (
          <p key={ev.chunk_id ?? ev.section ?? ev.text ?? "ev"} className="small">
            <strong>{ev.section ?? ev.chunk_id}</strong>
            {ev.page_reference ? ` · p.${ev.page_reference}` : ""} · {ev.source_url}
            <br />
            {ev.text}
          </p>
        ))
      )}

      <h3>Application route</h3>
      <p className="small">{item.application_route.url ?? "No URL on this demo record."}</p>
      <ul>
        {(item.application_route.steps ?? []).map((step) => (
          <li key={step} className="muted">
            {step}
          </li>
        ))}
      </ul>
    </article>
  );
}

export default function ResultsPage() {
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [result, setResult] = useState<EligibilityResult | null>(null);

  const loadStored = useCallback(async () => {
    const resultId = getStoredResultId();
    if (!resultId) {
      setResult(null);
      setLoading(false);
      return;
    }
    try {
      setResult(await getResult(resultId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load stored result.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadStored();
  }, [loadStored]);

  async function runEvaluation() {
    const profileId = getStoredProfileId();
    if (!profileId) {
      setError("Save a profile before evaluating.");
      return;
    }
    setEvaluating(true);
    setError(null);
    setSuccess(null);
    try {
      const created = await evaluateEligibility(profileId);
      const fetched = await getResult(created.id);
      setStoredResultId(fetched.id);
      setResult(fetched);
      setSuccess("Loaded result from GET /api/results/{id}.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Evaluation failed.");
    } finally {
      setEvaluating(false);
    }
  }

  return (
    <main className="shell">
      <p className="eyebrow">Decision support</p>
      <h1>Results</h1>
      <p className="lede">
        Eligibility statuses come from the Python rule engine. This page reads the stored
        result object from FastAPI.
      </p>
      {loading ? <p className="muted">Loading…</p> : null}
      {error ? <Banner tone="bad">{error}</Banner> : null}
      {success ? <Banner tone="ok">{success}</Banner> : null}

      <div className="actions">
        <button className="button" disabled={evaluating} onClick={() => void runEvaluation()}>
          {evaluating ? "Evaluating…" : "Run eligibility evaluation"}
        </button>
      </div>

      {!loading && !result ? (
        <section className="card">
          <h2>No result yet</h2>
          <p>Run evaluation after profile and documents are ready.</p>
        </section>
      ) : null}

      <div className="stack">
        {result?.policies.map((item) => (
          <PolicyResult key={item.policy_id} item={item} />
        ))}
      </div>
    </main>
  );
}

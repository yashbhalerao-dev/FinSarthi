"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Banner } from "@/components/Banner";
import { ApiError, searchPolicies } from "@/lib/api";
import { getStoredProfileId } from "@/lib/session";
import type { PolicyChunk, PolicyRecord } from "@/types/api";

export default function DiscoveryPage() {
  const [hasProfile, setHasProfile] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [policies, setPolicies] = useState<PolicyRecord[]>([]);
  const [chunks, setChunks] = useState<PolicyChunk[]>([]);

  useEffect(() => {
    const profileId = getStoredProfileId();
    setHasProfile(Boolean(profileId));
    if (!profileId) {
      setLoading(false);
      return;
    }
    searchPolicies(profileId)
      .then((data) => {
        setPolicies(data.policies);
        setChunks(data.chunks);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Discovery failed."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="shell">
      <p className="eyebrow">Retrieval</p>
      <h1>Policy discovery</h1>
      {loading ? <p className="muted">Searching policies…</p> : null}
      {error ? <Banner tone="bad">{error}</Banner> : null}
      {!hasProfile && !loading ? (
        <Banner tone="warn">
          Save a profile first. Discovery uses POST /api/policies/search.
        </Banner>
      ) : null}
      {!loading && hasProfile && policies.length === 0 ? (
        <section className="card">
          <h2>No matching policies</h2>
          <p>The retriever returned no synthetic demo policies for this profile.</p>
        </section>
      ) : null}

      <div className="stack">
        {policies.map((policy) => (
          <article className="card" key={policy.id}>
            {policy.synthetic ? <p className="eyebrow">Synthetic demo record</p> : null}
            <h2>{policy.name}</h2>
            <p>
              {policy.issuing_authority} · {policy.jurisdiction} · {policy.category}
            </p>
            <p className="small">
              Source: {policy.source_url} · {policy.source_document}
              {policy.version ? ` · version ${policy.version}` : ""}
            </p>
            <h3>Conditions in the policy record</h3>
            <ul>
              {(policy.conditions ?? []).map((condition, index) => (
                <li key={`${policy.id}-${index}`} className="muted">
                  {condition.field} {condition.operator} {String(condition.expected)}
                </li>
              ))}
            </ul>
            <p className="small">
              Required documents: {(policy.required_documents ?? []).join(", ") || "none listed"}
            </p>
          </article>
        ))}
      </div>

      {chunks.length > 0 ? (
        <section className="card" style={{ marginTop: "1.2rem" }}>
          <h2>Retrieved evidence chunks</h2>
          {chunks.map((chunk) => (
            <p key={chunk.id} className="small">
              <strong>{chunk.section ?? chunk.id}</strong> · {chunk.text}
            </p>
          ))}
        </section>
      ) : null}

      <div className="actions">
        <Link className="button" href="/results">
          Evaluate eligibility
        </Link>
      </div>
    </main>
  );
}

"use client";

import { FormEvent, useEffect, useState } from "react";
import { Banner } from "@/components/Banner";
import {
  ApiError,
  createProfile,
  getProfile,
  updateProfile,
} from "@/lib/api";
import { getStoredProfileId, setStoredProfileId } from "@/lib/session";
import type { ApplicantProfile, ApplicantType, ProfilePayload } from "@/types/api";

const EMPTY: ProfilePayload = {
  applicant_type: "individual",
  age: null,
  state: "",
  district: "",
  income: null,
  occupation: "",
  category: "",
  business_type: "",
  registration_status: "",
  turnover: null,
  investment: null,
  uncertain_fields: [],
  source_evidence: [],
};

function toForm(profile?: ApplicantProfile | null): ProfilePayload {
  if (!profile) return { ...EMPTY };
  return {
    applicant_type: profile.applicant_type,
    age: profile.age,
    state: profile.state ?? "",
    district: profile.district ?? "",
    income: profile.income,
    occupation: profile.occupation ?? "",
    category: profile.category ?? "",
    business_type: profile.business_type ?? "",
    registration_status: profile.registration_status ?? "",
    turnover: profile.turnover,
    investment: profile.investment,
    uncertain_fields: profile.uncertain_fields ?? [],
    source_evidence: profile.source_evidence ?? [],
  };
}

function clean(payload: ProfilePayload): ProfilePayload {
  const blankToNull = (value: string | null | undefined) => {
    if (value === undefined || value === null || value === "") return null;
    return value;
  };
  return {
    ...payload,
    state: blankToNull(payload.state ?? null),
    district: blankToNull(payload.district ?? null),
    occupation: blankToNull(payload.occupation ?? null),
    category: blankToNull(payload.category ?? null),
    business_type: blankToNull(payload.business_type ?? null),
    registration_status: blankToNull(payload.registration_status ?? null),
  };
}

export default function ProfilePage() {
  const [form, setForm] = useState<ProfilePayload>(EMPTY);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    const id = getStoredProfileId();
    if (!id) {
      setLoading(false);
      return;
    }
    getProfile(id)
      .then((profile) => {
        setProfileId(profile.id);
        setForm(toForm(profile));
      })
      .catch(() => {
        setError("Stored profile was not found. Create a new one.");
      })
      .finally(() => setLoading(false));
  }, []);

  function setType(applicant_type: ApplicantType) {
    setForm((current) => ({ ...current, applicant_type }));
  }

  function field<K extends keyof ProfilePayload>(key: K, value: ProfilePayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function numberField(key: "age" | "income" | "turnover" | "investment", raw: string) {
    field(key, raw === "" ? null : Number(raw));
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(null);
    const payload = clean(form);
    if (!payload.applicant_type) {
      setError("Select Individual or Small Business.");
      setSaving(false);
      return;
    }
    try {
      const saved = profileId
        ? await updateProfile(profileId, payload)
        : await createProfile(payload);
      setStoredProfileId(saved.id);
      setProfileId(saved.id);
      setForm(toForm(saved));
      setSuccess("Profile saved to FastAPI.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Save failed.");
    } finally {
      setSaving(false);
    }
  }

  const isBusiness = form.applicant_type === "small_business";

  return (
    <main className="shell">
      <p className="eyebrow">Applicant</p>
      <h1>Profile</h1>
      {loading ? <p className="muted">Loading…</p> : null}
      {error ? <Banner tone="bad">{error}</Banner> : null}
      {success ? <Banner tone="ok">{success}</Banner> : null}

      <form className="stack" onSubmit={onSubmit}>
        <div className="segment">
          <button type="button" className={!isBusiness ? "on" : ""} onClick={() => setType("individual")}>
            Individual
          </button>
          <button type="button" className={isBusiness ? "on" : ""} onClick={() => setType("small_business")}>
            Small Business
          </button>
        </div>

        <div className="form-grid">
          <label>
            State
            <input value={form.state ?? ""} onChange={(e) => field("state", e.target.value)} />
          </label>
          <label>
            District
            <input value={form.district ?? ""} onChange={(e) => field("district", e.target.value)} />
          </label>
          <label>
            Occupation
            <input value={form.occupation ?? ""} onChange={(e) => field("occupation", e.target.value)} />
          </label>
          {!isBusiness ? (
            <>
              <label>
                Age
                <input
                  type="number"
                  min={0}
                  max={120}
                  value={form.age ?? ""}
                  onChange={(e) => numberField("age", e.target.value)}
                />
              </label>
              <label>
                Annual income
                <input
                  type="number"
                  min={0}
                  value={form.income ?? ""}
                  onChange={(e) => numberField("income", e.target.value)}
                />
              </label>
              <label>
                Category
                <input value={form.category ?? ""} onChange={(e) => field("category", e.target.value)} />
              </label>
            </>
          ) : (
            <>
              <label>
                Business type
                <input
                  value={form.business_type ?? ""}
                  onChange={(e) => field("business_type", e.target.value)}
                />
              </label>
              <label>
                Registration status
                <input
                  value={form.registration_status ?? ""}
                  onChange={(e) => field("registration_status", e.target.value)}
                />
              </label>
              <label>
                Turnover
                <input
                  type="number"
                  min={0}
                  value={form.turnover ?? ""}
                  onChange={(e) => numberField("turnover", e.target.value)}
                />
              </label>
              <label>
                Investment
                <input
                  type="number"
                  min={0}
                  value={form.investment ?? ""}
                  onChange={(e) => numberField("investment", e.target.value)}
                />
              </label>
            </>
          )}
        </div>
        <div className="actions">
          <button className="button" type="submit" disabled={saving}>
            {saving ? "Saving…" : profileId ? "Update profile" : "Save profile"}
          </button>
        </div>
      </form>
    </main>
  );
}

import type {
  ApplicantProfile,
  DocumentRecord,
  EligibilityResult,
  PolicyChunk,
  PolicyRecord,
  ProfilePayload,
} from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(status: number, message: string, code?: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function parseError(response: Response): Promise<ApiError> {
  try {
    const body = await response.json();
    const detail = body.detail ?? body.error;
    if (typeof detail === "string") {
      return new ApiError(response.status, detail);
    }
    if (detail && typeof detail === "object") {
      return new ApiError(
        response.status,
        String(detail.message ?? "Request failed"),
        detail.code,
      );
    }
    return new ApiError(response.status, "Request failed");
  } catch {
    return new ApiError(response.status, response.statusText || "Request failed");
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    throw await parseError(response);
  }
  const body = (await response.json()) as { data: T };
  return body.data;
}

export function getApiBase(): string {
  return API_BASE;
}

export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/api/health`);
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json();
}

export function createProfile(payload: ProfilePayload): Promise<ApplicantProfile> {
  return request("/api/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function getProfile(profileId: string): Promise<ApplicantProfile> {
  return request(`/api/profile/${encodeURIComponent(profileId)}`);
}

export function updateProfile(
  profileId: string,
  payload: ProfilePayload,
): Promise<ApplicantProfile> {
  return request(`/api/profile/${encodeURIComponent(profileId)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function listDocuments(profileId: string): Promise<DocumentRecord[]> {
  return request(`/api/documents?profile_id=${encodeURIComponent(profileId)}`);
}

export async function uploadDocument(
  profileId: string,
  file: File,
): Promise<DocumentRecord> {
  const form = new FormData();
  form.append("profile_id", profileId);
  form.append("file", file);
  return request("/api/documents/upload", { method: "POST", body: form });
}

export function processDocument(
  documentId: string,
): Promise<{ document: DocumentRecord; profile: ApplicantProfile | null }> {
  return request("/api/documents/process", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId }),
  });
}

export function getDocument(documentId: string): Promise<DocumentRecord> {
  return request(`/api/documents/${encodeURIComponent(documentId)}`);
}

export function searchPolicies(
  profileId: string,
  query?: string,
): Promise<{ chunks: PolicyChunk[]; policies: PolicyRecord[] }> {
  return request("/api/policies/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile_id: profileId, query: query || null }),
  });
}

export function evaluateEligibility(profileId: string): Promise<EligibilityResult> {
  return request("/api/eligibility/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile_id: profileId }),
  });
}

export function getResult(resultId: string): Promise<EligibilityResult> {
  return request(`/api/results/${encodeURIComponent(resultId)}`);
}

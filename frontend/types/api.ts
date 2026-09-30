export type ApplicantType = "individual" | "small_business";
export type ExtractionStatus = "pending" | "processed" | "failed";
export type ConditionStatus = "SATISFIED" | "NOT_SATISFIED" | "NEEDS_VERIFICATION";
export type OverallStatus = "ELIGIBLE" | "NOT_ELIGIBLE" | "NEEDS_VERIFICATION";

export interface SourceEvidenceItem {
  field: string;
  value: unknown;
  source?: string | null;
}

export interface ApplicantProfile {
  id: string;
  applicant_type: ApplicantType;
  age: number | null;
  state: string | null;
  district: string | null;
  income: number | null;
  occupation: string | null;
  category: string | null;
  business_type: string | null;
  registration_status: string | null;
  turnover: number | null;
  investment: number | null;
  uncertain_fields: string[];
  source_evidence: SourceEvidenceItem[];
}

export interface ProfilePayload {
  id?: string;
  applicant_type: ApplicantType;
  age?: number | null;
  state?: string | null;
  district?: string | null;
  income?: number | null;
  occupation?: string | null;
  category?: string | null;
  business_type?: string | null;
  registration_status?: string | null;
  turnover?: number | null;
  investment?: number | null;
  uncertain_fields?: string[];
  source_evidence?: SourceEvidenceItem[];
}

export interface DocumentRecord {
  id: string;
  profile_id: string;
  filename: string;
  document_type: string;
  storage_reference: string;
  extraction_status: ExtractionStatus | string;
  extracted_fields: Record<string, unknown>;
  confidence: number;
  uncertain_fields: string[];
  uploaded_at: string;
}

export interface PolicyConditionSpec {
  field: string;
  operator: string;
  expected: unknown;
}

export interface PolicyRecord {
  id: string;
  name: string;
  issuing_authority: string;
  jurisdiction: string;
  category: string;
  applicant_type: string;
  source_url: string;
  source_document: string;
  version: string | null;
  effective_date: string | null;
  verified_at: string | null;
  status: string;
  conditions: PolicyConditionSpec[];
  required_documents: string[];
  benefit: {
    amount?: number | null;
    currency?: string | null;
    basis?: string | null;
    supported_by_source?: boolean;
  } | null;
  application_route: { url?: string | null; steps?: string[] };
  synthetic: boolean;
}

export interface PolicyChunk {
  id: string;
  policy_id: string;
  text: string;
  section: string | null;
  page_reference: string | null;
  metadata: Record<string, unknown>;
  embedding_id: string | null;
}

export interface ConditionResult {
  field: string;
  operator: string;
  expected: unknown;
  actual: unknown;
  status: ConditionStatus;
  evidence: string | null;
  reason: string | null;
}

export interface BenefitResult {
  amount: number | null;
  currency: string | null;
  basis: string | null;
  supported_by_source: boolean;
}

export interface EvidenceItem {
  policy_id: string;
  chunk_id: string | null;
  source_url: string;
  section: string | null;
  page_reference: string | null;
  text: string | null;
}

export interface ApplicationRoute {
  url: string | null;
  steps: string[];
}

export interface PolicyEvaluation {
  policy_id: string;
  policy_name: string;
  synthetic: boolean;
  overall_status: OverallStatus;
  conditions: ConditionResult[];
  benefit: BenefitResult;
  required_documents: string[];
  missing_documents: string[];
  evidence: EvidenceItem[];
  application_route: ApplicationRoute;
  review_required: boolean;
  explanation: string;
}

export interface EligibilityResult {
  id: string;
  profile_id: string;
  policies: PolicyEvaluation[];
}

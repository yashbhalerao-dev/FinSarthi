import type { ProfilePayload } from "@/types/api";

export interface DemoCase {
  id: "demo-a" | "demo-b" | "demo-c";
  label: string;
  expectedHint: string;
  profile: ProfilePayload;
  files: { filename: string; body: Record<string, unknown> }[];
}

export const DEMO_CASES: DemoCase[] = [
  {
    id: "demo-a",
    label: "Demo A",
    expectedHint: "Individual qualifying case (backend rules decide)",
    profile: {
      id: "demo-a",
      applicant_type: "individual",
      age: 28,
      state: "Maharashtra",
      district: "Pune",
      income: 200000,
      occupation: "salaried",
      uncertain_fields: [],
      source_evidence: [],
    },
    files: [
      {
        filename: "demo-a-income.json",
        body: {
          document_type: "income_certificate",
          confidence: 0.93,
          uncertain_fields: [],
          extracted_fields: {
            applicant_type: "individual",
            age: 28,
            state: "Maharashtra",
            district: "Pune",
            income: 200000,
            occupation: "salaried",
          },
        },
      },
      {
        filename: "demo-a-identity.json",
        body: {
          document_type: "identity_proof",
          confidence: 0.9,
          extracted_fields: { state: "Maharashtra" },
        },
      },
    ],
  },
  {
    id: "demo-b",
    label: "Demo B",
    expectedHint: "Small business failing a condition (backend rules decide)",
    profile: {
      id: "demo-b",
      applicant_type: "small_business",
      state: "Maharashtra",
      occupation: "owner",
      business_type: "trading",
      registration_status: "registered",
      turnover: 5000000,
      investment: 800000,
      uncertain_fields: [],
      source_evidence: [],
    },
    files: [
      {
        filename: "demo-b-registration.json",
        body: {
          document_type: "business_registration",
          confidence: 0.9,
          extracted_fields: {
            applicant_type: "small_business",
            state: "Maharashtra",
            business_type: "trading",
            registration_status: "registered",
            turnover: 5000000,
          },
        },
      },
      {
        filename: "demo-b-bank.json",
        body: { document_type: "bank_statement", confidence: 0.88, extracted_fields: {} },
      },
    ],
  },
  {
    id: "demo-c",
    label: "Demo C",
    expectedHint: "Missing/uncertain income (backend rules decide)",
    profile: {
      id: "demo-c",
      applicant_type: "individual",
      age: 41,
      state: "Maharashtra",
      occupation: "self-employed",
      uncertain_fields: ["income"],
      source_evidence: [],
    },
    files: [
      {
        filename: "demo-c-identity.json",
        body: {
          document_type: "identity_proof",
          confidence: 0.4,
          uncertain_fields: ["income"],
          extracted_fields: {
            applicant_type: "individual",
            age: 41,
            state: "Maharashtra",
            occupation: "self-employed",
          },
        },
      },
    ],
  },
];

export function jsonFile(filename: string, body: Record<string, unknown>): File {
  return new File([JSON.stringify(body, null, 2)], filename, { type: "application/json" });
}

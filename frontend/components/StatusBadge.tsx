import type { OverallStatus } from "@/types/api";

export function StatusBadge({
  status,
}: {
  status?: string | OverallStatus | null;
}) {
  if (!status) return <span className="badge">Unknown</span>;
  const tone =
    status === "ELIGIBLE" || status === "SATISFIED" || status === "processed"
      ? "ok"
      : status === "NOT_ELIGIBLE" || status === "NOT_SATISFIED" || status === "failed"
        ? "bad"
        : status === "NEEDS_VERIFICATION" || status === "pending"
          ? "warn"
          : "neutral";
  return <span className={`badge badge-${tone}`}>{status.replace(/_/g, " ")}</span>;
}

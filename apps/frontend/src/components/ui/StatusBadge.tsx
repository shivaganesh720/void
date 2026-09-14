import type { ReactNode } from "react";

const toneFor = (value: string) => {
  const normalized = value.toUpperCase();
  if (/(COMPLETED|APPROVED|AVAILABLE|PASSED|SUCCESS)/.test(normalized)) return "success";
  if (/(FAILED|BLOCKED|REJECTED|ERROR|CRITICAL)/.test(normalized)) return "danger";
  if (/(WAIT|PAUSED|PENDING|WARNING|HIGH)/.test(normalized)) return "warning";
  if (/(RUNNING|READY|INFO|AUTO)/.test(normalized)) return "info";
  return "neutral";
};

export function StatusBadge({ value, children }: { value: string; children?: ReactNode }) {
  return <span className={`status-badge ${toneFor(value)}`}>{children ?? value.replaceAll("_", " ")}</span>;
}

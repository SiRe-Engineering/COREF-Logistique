import type { ReactNode } from "react";

type Tone = "neutral" | "success" | "beton" | "isolants" | "warning";

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: Tone;
}) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

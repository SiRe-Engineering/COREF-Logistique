import type { ReactNode } from "react";
import styles from "./KpiGrid.module.css";

export function KpiGrid({ children }: { children: ReactNode }) {
  return <section className={styles.grid}>{children}</section>;
}

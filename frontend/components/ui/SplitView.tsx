import type { ReactNode } from "react";
import styles from "./SplitView.module.css";

type SplitViewProps = {
  master: ReactNode;
  detail: ReactNode;
  detailOpen?: boolean;
};

export function SplitView({
  master,
  detail,
  detailOpen = true,
}: SplitViewProps) {
  return (
    <section
      className={`${styles.layout} ${
        detailOpen ? styles.open : styles.closed
      }`}
    >
      <aside className={styles.master}>{master}</aside>
      <main className={styles.detail}>{detail}</main>
    </section>
  );
}

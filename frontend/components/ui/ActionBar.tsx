import type { ReactNode } from "react";
import styles from "./ActionBar.module.css";

type ActionBarProps = {
  children: ReactNode;
  secondary?: ReactNode;
  sticky?: boolean;
};

export function ActionBar({
  children,
  secondary,
  sticky = false,
}: ActionBarProps) {
  return (
    <div className={`${styles.bar} ${sticky ? styles.sticky : ""}`}>
      <div className={styles.secondary}>{secondary}</div>
      <div className={styles.primary}>{children}</div>
    </div>
  );
}

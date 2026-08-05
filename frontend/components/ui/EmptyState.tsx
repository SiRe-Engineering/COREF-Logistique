import type { ReactNode } from "react";
import styles from "./EmptyState.module.css";

type EmptyStateProps = {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
};

export function EmptyState({
  icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className={styles.empty}>
      {icon && <div className={styles.icon}>{icon}</div>}
      <strong>{title}</strong>
      {description && <p>{description}</p>}
      {action}
    </div>
  );
}

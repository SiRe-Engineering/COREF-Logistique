import type { ReactNode } from "react";
import styles from "./KpiCard.module.css";

type KpiCardProps = {
  label: string;
  value: ReactNode;
  description?: string;
  icon?: ReactNode;
};

export function KpiCard({
  label,
  value,
  description,
  icon,
}: KpiCardProps) {
  return (
    <article className={styles.card}>
      {icon && <div className={styles.icon}>{icon}</div>}
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        {description && <small>{description}</small>}
      </div>
    </article>
  );
}

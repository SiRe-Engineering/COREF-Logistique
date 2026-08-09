import styles from "./StatusBadge.module.css";

export type StatusTone =
  | "neutral"
  | "information"
  | "pending"
  | "success"
  | "warning"
  | "danger"
  | "validation";

type StatusBadgeProps = {
  label: string;
  tone?: StatusTone;
};

export function StatusBadge({
  label,
  tone = "neutral",
}: StatusBadgeProps) {
  return (
    <span className={`${styles.badge} ${styles[tone]}`}>
      <span aria-hidden="true" />
      {label}
    </span>
  );
}

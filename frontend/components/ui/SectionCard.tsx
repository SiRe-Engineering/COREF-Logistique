import type { ReactNode } from "react";
import styles from "./SectionCard.module.css";

type SectionCardProps = {
  title?: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  flush?: boolean;
};

export function SectionCard({
  title,
  description,
  actions,
  children,
  flush = false,
}: SectionCardProps) {
  return (
    <section className={styles.card}>
      {(title || description || actions) && (
        <header className={styles.header}>
          <div>
            {title && <h3>{title}</h3>}
            {description && <p>{description}</p>}
          </div>
          {actions && <div className={styles.actions}>{actions}</div>}
        </header>
      )}

      <div className={flush ? styles.flush : styles.content}>
        {children}
      </div>
    </section>
  );
}

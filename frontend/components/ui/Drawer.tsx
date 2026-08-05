"use client";

import type { ReactNode } from "react";
import { X } from "lucide-react";
import styles from "./Drawer.module.css";

type DrawerSize = "medium" | "wide" | "workspace";

type DrawerProps = {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
  eyebrow?: string;
  size?: DrawerSize;
  footer?: ReactNode;
};

export function Drawer({
  open,
  title,
  onClose,
  children,
  eyebrow = "Fiche détaillée",
  size = "wide",
  footer,
}: DrawerProps) {
  if (!open) return null;

  return (
    <div className={styles.layer} role="presentation">
      <button
        className={styles.backdrop}
        aria-label="Fermer le panneau"
        onClick={onClose}
      />

      <aside
        className={`${styles.drawer} ${styles[size]}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <header className={styles.header}>
          <div>
            <span className="eyebrow">{eyebrow}</span>
            <h2>{title}</h2>
          </div>

          <button
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Fermer"
          >
            <X size={20} />
          </button>
        </header>

        <div className={styles.content}>{children}</div>

        {footer && <footer className={styles.footer}>{footer}</footer>}
      </aside>
    </div>
  );
}

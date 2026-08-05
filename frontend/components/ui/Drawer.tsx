"use client";

import type { ReactNode } from "react";
import { X } from "lucide-react";

export function Drawer({
  open,
  title,
  onClose,
  children,
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  if (!open) return null;

  return (
    <div className="drawer-layer" role="presentation">
      <button
        className="drawer-backdrop"
        aria-label="Fermer le panneau"
        onClick={onClose}
      />
      <aside className="drawer" role="dialog" aria-modal="true">
        <header className="drawer-header">
          <div>
            <span className="eyebrow">Fiche détaillée</span>
            <h2>{title}</h2>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Fermer">
            <X size={18} />
          </button>
        </header>
        <div className="drawer-content">{children}</div>
      </aside>
    </div>
  );
}

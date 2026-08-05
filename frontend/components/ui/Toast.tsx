"use client";

import { CheckCircle2, CircleAlert, X } from "lucide-react";

export function Toast({
  message,
  type,
  onClose,
}: {
  message: string;
  type: "success" | "error";
  onClose: () => void;
}) {
  return (
    <div className={`toast toast-${type}`} role="status">
      {type === "success" ? (
        <CheckCircle2 size={19} />
      ) : (
        <CircleAlert size={19} />
      )}
      <span>{message}</span>
      <button onClick={onClose} aria-label="Fermer">
        <X size={16} />
      </button>
    </div>
  );
}

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FileCheck2,
  Hammer,
  UserRoundCheck,
  Wrench,
} from "lucide-react";

import styles from "./MaterielTabs.module.css";

const onglets = [
  {
    href: "/materiels",
    label: "Parc matériel",
    icon: Hammer,
  },
  {
    href: "/prets-materiel",
    label: "Prêts & déplacements",
    icon: UserRoundCheck,
  },
  {
    href: "/maintenance-materiel",
    label: "Maintenance & contrôles",
    icon: Wrench,
  },
  {
    href: "/documents-materiel",
    label: "Documents & conformité",
    icon: FileCheck2,
  },
];

export function MaterielTabs() {
  const pathname = usePathname();

  return (
    <nav
      className={styles.tabs}
      aria-label="Navigation du module matériels"
    >
      {onglets.map(({ href, label, icon: Icon }) => {
        const actif =
          pathname === href ||
          (href !== "/materiels" && pathname.startsWith(`${href}/`));

        return (
          <Link
            key={href}
            href={href}
            className={actif ? styles.active : undefined}
          >
            <Icon size={16} />
            <span>{label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

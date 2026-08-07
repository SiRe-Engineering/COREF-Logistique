"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Boxes,
  BriefcaseBusiness,
  ClipboardCheck,
  ClipboardList,
  Construction,
  FlaskConical,
  Gauge,
  Hammer,
  MapPin,
  ScanLine,
  PackageCheck,
  PackageSearch,
  Settings,
  Shapes,
  Truck,
  Users,
  Warehouse,
} from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";

export function Sidebar() {
  const pathname = usePathname();
  const { utilisateur } = useAuth();

  const peutGererUtilisateurs = [
    "ADMINISTRATEUR_TECHNIQUE",
    "ADMINISTRATEUR_COREF",
  ].includes(utilisateur.role);

  const navigation = [
    { href: "/", label: "Tableau de bord", icon: Gauge },
    { href: "/articles", label: "Articles", icon: PackageSearch },
    { href: "#", label: "Familles", icon: Shapes, disabled: true },
    { href: "/stocks", label: "Stocks", icon: Warehouse },
    { href: "/magasin", label: "Mode magasin", icon: ScanLine },
    { href: "/mouvements", label: "Mouvements", icon: Boxes },
    { href: "/demandes-sortie", label: "Demandes de sortie", icon: ClipboardList },
    { href: "/inventaires", label: "Inventaires", icon: ClipboardCheck },
    { href: "/preparations", label: "Préparations / Retours", icon: PackageCheck },
    { href: "/affaires", label: "Affaires", icon: BriefcaseBusiness },
    { href: "/lots-beton", label: "Lots béton", icon: FlaskConical },
    { href: "/materiels", label: "Matériels", icon: Hammer },
    { href: "#", label: "Moules", icon: Construction, disabled: true },
    { href: "#", label: "Véhicules", icon: Truck, disabled: true },
    { href: "/emplacements", label: "Emplacements", icon: MapPin },
    ...(peutGererUtilisateurs
      ? [
          {
            href: "/administration/utilisateurs",
            label: "Utilisateurs",
            icon: Users,
          },
        ]
      : []),
    ...(utilisateur.role === "ADMINISTRATEUR_TECHNIQUE"
      ? [
          {
            href: "#",
            label: "Système",
            icon: Settings,
            disabled: true,
          },
        ]
      : []),
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">CL</div>
        <div>
          <strong>COREF</strong>
          <span>Logistique</span>
        </div>
      </div>

      <nav className="navigation" aria-label="Navigation principale">
        {navigation.map((item) => {
          const Icon = item.icon;
          const active =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href) && item.href !== "#";

          if (item.disabled) {
            return (
              <span className="nav-link nav-link-disabled" key={item.label}>
                <Icon size={18} strokeWidth={1.8} />
                <span>{item.label}</span>
                <small>Bientôt</small>
              </span>
            );
          }

          return (
            <Link
              className={`nav-link ${active ? "nav-link-active" : ""}`}
              href={item.href}
              key={item.label}
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <span className="system-dot" />
        {utilisateur.type_compte === "TECHNIQUE"
          ? "Administration technique"
          : "Espace COREF"}
      </div>
    </aside>
  );
}

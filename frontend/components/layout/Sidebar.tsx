"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Boxes,
  BellRing,
  BriefcaseBusiness,
  ClipboardCheck,
  ClipboardList,
  FlaskConical,
  Gauge,
  Hammer,
  MapPin,
  ScanLine,
  PackageCheck,
  PackageSearch,
  ShoppingCart,
  Building2,
  ChartNoAxesCombined,
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
    { href: "/alertes", label: "Alertes", icon: BellRing },
    { href: "/articles", label: "Articles", icon: PackageSearch },
    { href: "/stocks", label: "Stocks", icon: Warehouse },
    { href: "/reapprovisionnement", label: "Réapprovisionnement", icon: ShoppingCart },
    { href: "/achats", label: "Fournisseurs / Achats", icon: Building2 },
    { href: "/valorisation", label: "Valorisation", icon: ChartNoAxesCombined },
    { href: "/magasin", label: "Mode magasin", icon: ScanLine },
    { href: "/mouvements", label: "Mouvements", icon: Boxes },
    { href: "/demandes-sortie", label: "Demandes de sortie", icon: ClipboardList },
    { href: "/inventaires", label: "Inventaires", icon: ClipboardCheck },
    { href: "/preparations", label: "Préparations / Retours", icon: PackageCheck },
    { href: "/affaires", label: "Affaires", icon: BriefcaseBusiness },
    { href: "/lots-beton", label: "Lots béton", icon: FlaskConical },
    { href: "/materiels", label: "Matériels", icon: Hammer },
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

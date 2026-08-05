"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Boxes,
  ClipboardCheck,
  Construction,
  Gauge,
  Hammer,
  MapPin,
  PackageSearch,
  Settings,
  Shapes,
  Truck,
  Warehouse,
} from "lucide-react";

const navigation = [
  { href: "/", label: "Tableau de bord", icon: Gauge },
  { href: "/articles", label: "Articles", icon: PackageSearch },
  { href: "#", label: "Familles", icon: Shapes, disabled: true },
  { href: "#", label: "Stocks", icon: Warehouse, disabled: true },
  { href: "#", label: "Mouvements", icon: Boxes, disabled: true },
  { href: "#", label: "Inventaires", icon: ClipboardCheck, disabled: true },
  { href: "#", label: "Matériels", icon: Hammer, disabled: true },
  { href: "#", label: "Moules", icon: Construction, disabled: true },
  { href: "#", label: "Véhicules", icon: Truck, disabled: true },
  { href: "/emplacements", label: "Emplacements", icon: MapPin },
  { href: "#", label: "Administration", icon: Settings, disabled: true },
];

export function Sidebar() {
  const pathname = usePathname();

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
        Environnement local
      </div>
    </aside>
  );
}

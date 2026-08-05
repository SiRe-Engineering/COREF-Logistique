import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "COREF Logistique",
  description: "Gestion des articles, stocks, matériels et moules de COREF",
};

const navigation = [
  { href: "/", label: "Tableau de bord", symbol: "⌂" },
  { href: "/articles", label: "Articles", symbol: "▣" },
  { href: "#", label: "Familles", symbol: "▤", disabled: true },
  { href: "#", label: "Stocks", symbol: "◫", disabled: true },
  { href: "#", label: "Mouvements", symbol: "⇄", disabled: true },
  { href: "#", label: "Inventaires", symbol: "✓", disabled: true },
  { href: "#", label: "Matériels", symbol: "⚒", disabled: true },
  { href: "#", label: "Moules", symbol: "◇", disabled: true },
  { href: "#", label: "Véhicules", symbol: "▰", disabled: true },
  { href: "#", label: "Chantiers", symbol: "⌁", disabled: true },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body>
        <div className="application-shell">
          <aside className="sidebar">
            <div className="brand">
              <div className="brand-mark">CL</div>
              <div>
                <strong>COREF</strong>
                <span>Logistique</span>
              </div>
            </div>

            <nav className="navigation" aria-label="Navigation principale">
              {navigation.map((item) =>
                item.disabled ? (
                  <span className="nav-link nav-link-disabled" key={item.label}>
                    <span className="nav-symbol">{item.symbol}</span>
                    {item.label}
                    <small>Bientôt</small>
                  </span>
                ) : (
                  <Link className="nav-link" href={item.href} key={item.label}>
                    <span className="nav-symbol">{item.symbol}</span>
                    {item.label}
                  </Link>
                )
              )}
            </nav>

            <div className="sidebar-footer">
              <span className="system-dot" />
              Environnement local
            </div>
          </aside>

          <div className="main-column">
            <header className="topbar">
              <div>
                <strong>COREF Logistique</strong>
                <span>Référentiel et flux logistiques</span>
              </div>
              <div className="topbar-actions">
                <span className="version-badge">V1.0</span>
                <div className="avatar">SG</div>
              </div>
            </header>

            <main className="page-content">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}

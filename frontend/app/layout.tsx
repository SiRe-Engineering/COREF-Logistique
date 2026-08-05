import type { Metadata } from "next";
import { Sidebar } from "@/components/layout/Sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "COREF Logistique",
  description: "Gestion des articles, stocks, matériels et moules de COREF",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body>
        <div className="application-shell">
          <Sidebar />

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

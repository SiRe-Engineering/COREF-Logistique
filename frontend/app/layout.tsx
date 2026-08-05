import type { Metadata } from "next";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { Sidebar } from "@/components/layout/Sidebar";
import { UserMenu } from "@/components/layout/UserMenu";
import "./globals.css";

export const metadata: Metadata = {
  title: "COREF Logistique",
  description: "Gestion des articles, stocks et matériels de COREF",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body>
        <AuthProvider>
          <div className="application-shell">
            <Sidebar />

            <div className="main-column">
              <header className="topbar">
                <div>
                  <strong>COREF Logistique</strong>
                  <span>Référentiel et flux logistiques</span>
                </div>
                <div className="topbar-actions">
                  <UserMenu />
                </div>
              </header>

              <main className="page-content">{children}</main>
            </div>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "COREF Logistique",
  description: "Gestion des stocks, inventaires et matériels",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body>
        <header>
          <strong>COREF Logistique</strong>
        </header>
        {children}
      </body>
    </html>
  );
}

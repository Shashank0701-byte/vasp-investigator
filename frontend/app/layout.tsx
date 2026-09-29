import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "Tracepoint · VASP Investigator",
  description: "Explainable blockchain evidence and service attribution",
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

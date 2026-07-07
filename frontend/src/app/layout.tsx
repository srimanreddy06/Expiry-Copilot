import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Expiry Copilot — Enterprise Inventory Waste Intelligence Platform",
  description:
    "Expiry Copilot leverages advanced Artificial Intelligence to track batches, predict expirations, forecast customer demand, recommend clearance discounts, and prevent waste for pharmacies, supermarkets, and hospitals.",
  keywords: [
    "Inventory Intelligence",
    "Expiry Prediction",
    "Waste Prevention",
    "FEFO tracking",
    "AI Copilot",
    "Retail Operations",
    "Pharmacy Inventory",
  ],
  authors: [{ name: "Expiry Copilot Inc." }],
};

export const viewport: Viewport = {
  themeColor: "#09090B",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full bg-brand-bg text-zinc-100 selection:bg-brand-primary selection:text-brand-bg overflow-x-hidden">
        {children}
        <Script src="https://accounts.google.com/gsi/client" async defer />
      </body>
    </html>
  );
}

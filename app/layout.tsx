import type { Metadata } from "next";
import { AppProviders } from "@/components/shell/app-providers";
import "./globals.css";

// Temporarily disabled Google Fonts due to network issues
// import { Cormorant_Garamond, Manrope } from "next/font/google";

// const display = Cormorant_Garamond({
//   variable: "--font-display",
//   subsets: ["latin"],
//   weight: ["500", "600", "700"],
// });

// const body = Manrope({
//   variable: "--font-body",
//   subsets: ["latin"],
//   weight: ["400", "500", "600", "700"],
// });

export const metadata: Metadata = {
  title: "EduDrive CRM",
  description: "A multi-tenant school operations and parent engagement platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-[#0b1225] font-sans text-[#f6f1e8]" suppressHydrationWarning>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}

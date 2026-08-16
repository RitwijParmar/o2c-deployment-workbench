import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "O2C Deployment Workbench | ERP Receivables Implementation",
  description: "A complete synthetic O2C customer implementation with configurable cash matching, collections, MCP, multi-agent operations, observability, UAT, and go-live controls.",
  icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
  openGraph: {
    title: "O2C Deployment Workbench",
    description: "ERP receivables implementation—from source mapping to governed agent operations.",
    type: "website",
    images: [{ url: "/og.png", width: 1536, height: 1024, alt: "O2C Deployment Workbench implementation overview" }],
  },
  twitter: { card: "summary_large_image", title: "O2C Deployment Workbench", description: "A complete synthetic ERP receivables implementation.", images: ["/og.png"] },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

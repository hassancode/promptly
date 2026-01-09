import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import Navigation from "@/components/Navigation";
import { SkipToContent, AnnouncementProvider } from "@/components/accessibility";

/**
 * Root layout with SEO metadata
 * Tasks: T031, T206 [Phase 2, Phase 9]
 */

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://promptly.ai";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Promptly - AI Search Visibility Platform",
    template: "%s | Promptly",
  },
  description:
    "Discover how your brand appears in AI-generated answers from ChatGPT, Claude, Gemini and more. Get competitive insights and actionable recommendations to improve your AI visibility.",
  keywords: [
    "AI visibility",
    "brand monitoring",
    "AI search",
    "ChatGPT",
    "Claude",
    "Gemini",
    "AI competitive analysis",
    "brand intelligence",
    "AI-generated content",
    "search visibility",
  ],
  authors: [{ name: "Promptly" }],
  creator: "Promptly",
  publisher: "Promptly",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteUrl,
    siteName: "Promptly",
    title: "Promptly - AI Search Visibility Platform",
    description:
      "Discover how your brand appears in AI-generated answers. Get competitive insights and actionable recommendations.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Promptly - AI Search Visibility Platform",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Promptly - AI Search Visibility Platform",
    description:
      "Discover how your brand appears in AI-generated answers. Get competitive insights and actionable recommendations.",
    images: ["/og-image.png"],
    creator: "@promptlyai",
  },
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/icon.svg", type: "image/svg+xml" },
    ],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180" }],
  },
  manifest: "/manifest.json",
  alternates: {
    canonical: siteUrl,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0f172a" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-black`}>
        <AuthProvider>
          <AnnouncementProvider>
            <SkipToContent />
            <Navigation />
            <main id="main-content" tabIndex={-1}>
              {children}
            </main>
          </AnnouncementProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

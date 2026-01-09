import type { Metadata } from "next";

/**
 * Login page layout with SEO metadata
 * Task: T206 [Phase 9]
 */

export const metadata: Metadata = {
  title: "Sign In",
  description:
    "Sign in to your Promptly account to track your brand's AI visibility across ChatGPT, Claude, Gemini and more.",
  openGraph: {
    title: "Sign In to Promptly",
    description:
      "Access your AI visibility dashboard and competitive insights.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function LoginLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

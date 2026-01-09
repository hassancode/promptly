import type { Metadata } from "next";

/**
 * Register page layout with SEO metadata
 * Task: T206 [Phase 9]
 */

export const metadata: Metadata = {
  title: "Create Account",
  description:
    "Create your free Promptly account and start tracking how your brand appears in AI-generated answers from ChatGPT, Claude, Gemini and more.",
  openGraph: {
    title: "Create Your Promptly Account",
    description:
      "Start tracking your brand's AI visibility for free. Monitor how AI models mention your brand.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RegisterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

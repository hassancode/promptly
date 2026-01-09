"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function Home() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-zinc-400">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center p-8">
      <main className="flex max-w-5xl flex-col items-center gap-12 text-center">
        {/* Hero Section */}
        <div className="space-y-6">
          <h1 className="text-6xl font-bold text-white sm:text-7xl">
            Understand Your{" "}
            <span className="bg-gradient-to-r from-brand-primary to-brand-accent bg-clip-text text-transparent">
              AI Visibility
            </span>
          </h1>
          <p className="mx-auto max-w-2xl text-xl text-zinc-400">
            Discover how your brand appears in AI-generated answers. Get
            competitive insights and evidence-backed recommendations to improve
            your visibility in AI search results.
          </p>
        </div>

        {/* CTA Buttons */}
        {user ? (
          <div className="flex flex-col gap-4 sm:flex-row">
            <Link
              href="/dashboard"
              className="rounded-lg bg-brand-primary px-8 py-4 text-lg font-semibold text-white shadow-lg shadow-brand-primary/50 transition-all hover:bg-brand-secondary hover:shadow-brand-secondary/50"
            >
              Go to Dashboard
            </Link>
          </div>
        ) : (
          <div className="flex flex-col gap-4 sm:flex-row">
            <Link
              href="/register"
              className="rounded-lg bg-brand-primary px-8 py-4 text-lg font-semibold text-white shadow-lg shadow-brand-primary/50 transition-all hover:bg-brand-secondary hover:shadow-brand-secondary/50"
            >
              Get Started Free
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-zinc-700 bg-zinc-900/50 px-8 py-4 text-lg font-semibold text-white backdrop-blur-sm transition-all hover:border-zinc-600 hover:bg-zinc-800/50"
            >
              Sign In
            </Link>
          </div>
        )}

        {/* Features Grid */}
        <div className="mt-12 grid gap-8 sm:grid-cols-3">
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/30 p-6 backdrop-blur-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-brand-primary/10">
              <svg
                className="h-6 w-6 text-brand-primary"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="mb-2 text-lg font-semibold text-white">
              Multi-AI Analysis
            </h3>
            <p className="text-sm text-zinc-400">
              Query OpenAI, Claude, Gemini, Perplexity, and more to understand
              your brand presence across AI platforms.
            </p>
          </div>

          <div className="rounded-lg border border-zinc-800 bg-zinc-900/30 p-6 backdrop-blur-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-brand-accent/10">
              <svg
                className="h-6 w-6 text-brand-accent"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="mb-2 text-lg font-semibold text-white">
              Competitive Insights
            </h3>
            <p className="text-sm text-zinc-400">
              Compare your brand against competitors with detailed visibility,
              sentiment, and mention analysis.
            </p>
          </div>

          <div className="rounded-lg border border-zinc-800 bg-zinc-900/30 p-6 backdrop-blur-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-brand-secondary/10">
              <svg
                className="h-6 w-6 text-brand-secondary"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="mb-2 text-lg font-semibold text-white">
              Actionable Recommendations
            </h3>
            <p className="text-sm text-zinc-400">
              Get evidence-backed, specific recommendations to improve your AI
              search visibility and sentiment.
            </p>
          </div>
        </div>

        {/* Supported Platforms */}
        <div className="mt-8 space-y-4">
          <p className="text-sm font-medium text-zinc-500">
            Supported AI Platforms
          </p>
          <div className="flex flex-wrap items-center justify-center gap-6 text-zinc-400">
            <span>OpenAI</span>
            <span className="text-zinc-700">•</span>
            <span>Claude</span>
            <span className="text-zinc-700">•</span>
            <span>Google Gemini</span>
            <span className="text-zinc-700">•</span>
            <span>Perplexity</span>
            <span className="text-zinc-700">•</span>
            <span>Google AI Search</span>
            <span className="text-zinc-700">•</span>
            <span>Hugging Face</span>
          </div>
        </div>
      </main>
    </div>
  );
}

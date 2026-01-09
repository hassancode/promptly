"use client";

import { useAuth } from "@/lib/auth-context";
import { ProtectedRoute } from "@/lib/protected-route";
import Link from "next/link";

function DashboardContent() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-7xl p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="mt-2 text-zinc-400">
          Welcome back, {user?.email}
        </p>
      </div>

      {/* Empty State */}
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="max-w-md text-center">
          {/* Illustration Icon */}
          <div className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-brand-primary/10">
            <svg
              className="h-12 w-12 text-brand-primary"
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

          {/* Empty State Text */}
          <h2 className="text-2xl font-bold text-white">
            No Analyses Yet
          </h2>
          <p className="mt-2 text-zinc-400">
            Start your first AI visibility analysis to see how your brand appears
            in AI-generated answers
          </p>

          {/* CTA Button */}
          <Link
            href="/dashboard/new-analysis"
            className="mt-8 inline-flex items-center gap-2 rounded-lg bg-brand-primary px-6 py-3 font-semibold text-white shadow-lg shadow-brand-primary/50 transition-all hover:bg-brand-secondary hover:shadow-brand-secondary/50"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M12 4v16m8-8H4" />
            </svg>
            Start New Analysis
          </Link>

          {/* Help Text */}
          <p className="mt-6 text-sm text-zinc-500">
            You'll be able to analyze your brand visibility across multiple AI
            platforms and get actionable insights
          </p>
        </div>
      </div>

      {/* Future: Analytics cards would go here */}
      {/*
      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
          <h3 className="text-lg font-semibold text-white">Total Analyses</h3>
          <p className="mt-2 text-3xl font-bold text-brand-primary">0</p>
        </div>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
          <h3 className="text-lg font-semibold text-white">Average Visibility</h3>
          <p className="mt-2 text-3xl font-bold text-brand-accent">-</p>
        </div>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6">
          <h3 className="text-lg font-semibold text-white">Insights Generated</h3>
          <p className="mt-2 text-3xl font-bold text-brand-secondary">0</p>
        </div>
      </div>
      */}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}

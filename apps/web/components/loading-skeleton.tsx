"use client";

/**
 * Loading skeleton components for async operations
 * Task: T202 [Phase 9]
 */

import React from "react";

// Base skeleton with shimmer animation
export function Skeleton({
  className = "",
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`animate-pulse bg-gray-200 rounded ${className}`}
      {...props}
    />
  );
}

// Text line skeleton
export function SkeletonText({
  lines = 1,
  className = "",
}: {
  lines?: number;
  className?: string;
}) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={`h-4 ${i === lines - 1 && lines > 1 ? "w-3/4" : "w-full"}`}
        />
      ))}
    </div>
  );
}

// Card skeleton for dashboard cards
export function SkeletonCard({ className = "" }: { className?: string }) {
  return (
    <div
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}
    >
      <div className="flex items-center justify-between mb-4">
        <Skeleton className="h-6 w-1/3" />
        <Skeleton className="h-6 w-6 rounded-full" />
      </div>
      <SkeletonText lines={2} />
      <div className="mt-4 flex gap-2">
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-8 w-20" />
      </div>
    </div>
  );
}

// Analysis list item skeleton
export function SkeletonAnalysisItem({ className = "" }: { className?: string }) {
  return (
    <div
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 ${className}`}
    >
      <div className="flex items-start gap-4">
        <Skeleton className="h-12 w-12 rounded-lg flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <Skeleton className="h-5 w-1/2 mb-2" />
          <Skeleton className="h-4 w-3/4 mb-2" />
          <div className="flex gap-2">
            <Skeleton className="h-5 w-16 rounded-full" />
            <Skeleton className="h-5 w-16 rounded-full" />
            <Skeleton className="h-5 w-16 rounded-full" />
          </div>
        </div>
        <Skeleton className="h-8 w-8 rounded flex-shrink-0" />
      </div>
    </div>
  );
}

// Analysis list skeleton
export function SkeletonAnalysisList({
  count = 3,
  className = "",
}: {
  count?: number;
  className?: string;
}) {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonAnalysisItem key={i} />
      ))}
    </div>
  );
}

// Provider status card skeleton
export function SkeletonProviderCard({ className = "" }: { className?: string }) {
  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}
    >
      <div className="flex items-center gap-3 mb-3">
        <Skeleton className="h-8 w-8 rounded" />
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-5 w-16 rounded-full ml-auto" />
      </div>
      <Skeleton className="h-2 w-full rounded-full mb-2" />
      <SkeletonText lines={2} />
    </div>
  );
}

// Provider grid skeleton
export function SkeletonProviderGrid({
  count = 6,
  className = "",
}: {
  count?: number;
  className?: string;
}) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonProviderCard key={i} />
      ))}
    </div>
  );
}

// Insight card skeleton
export function SkeletonInsightCard({ className = "" }: { className?: string }) {
  return (
    <div
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}
    >
      <div className="flex items-center gap-3 mb-4">
        <Skeleton className="h-10 w-10 rounded-full" />
        <div className="flex-1">
          <Skeleton className="h-5 w-1/3 mb-1" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </div>
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-6 w-16 rounded" />
        </div>
        <Skeleton className="h-3 w-full rounded-full" />
        <SkeletonText lines={3} />
      </div>
    </div>
  );
}

// Visibility score skeleton
export function SkeletonVisibilityScore({ className = "" }: { className?: string }) {
  return (
    <div className={`text-center ${className}`}>
      <Skeleton className="h-24 w-24 rounded-full mx-auto mb-4" />
      <Skeleton className="h-6 w-32 mx-auto mb-2" />
      <Skeleton className="h-4 w-48 mx-auto" />
    </div>
  );
}

// Chart skeleton
export function SkeletonChart({
  height = 200,
  className = "",
}: {
  height?: number;
  className?: string;
}) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
      <Skeleton className="h-5 w-1/4 mb-4" />
      <div className="flex items-end gap-2" style={{ height }}>
        {Array.from({ length: 7 }).map((_, i) => (
          <Skeleton
            key={i}
            className="flex-1"
            style={{ height: `${30 + Math.random() * 70}%` }}
          />
        ))}
      </div>
      <div className="flex justify-between mt-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <Skeleton key={i} className="h-3 w-8" />
        ))}
      </div>
    </div>
  );
}

// Recommendation item skeleton
export function SkeletonRecommendation({ className = "" }: { className?: string }) {
  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}
    >
      <div className="flex items-start gap-3">
        <Skeleton className="h-6 w-6 rounded flex-shrink-0 mt-1" />
        <div className="flex-1">
          <Skeleton className="h-5 w-3/4 mb-2" />
          <SkeletonText lines={2} />
          <div className="flex gap-2 mt-3">
            <Skeleton className="h-5 w-12 rounded-full" />
            <Skeleton className="h-5 w-16 rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
}

// Recommendations list skeleton
export function SkeletonRecommendationsList({
  count = 5,
  className = "",
}: {
  count?: number;
  className?: string;
}) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonRecommendation key={i} />
      ))}
    </div>
  );
}

// Table skeleton
export function SkeletonTable({
  rows = 5,
  columns = 4,
  className = "",
}: {
  rows?: number;
  columns?: number;
  className?: string;
}) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="flex gap-4 p-4 bg-gray-50 border-b border-gray-200">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={rowIndex}
          className="flex gap-4 p-4 border-b border-gray-100 last:border-b-0"
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

// Full page loading skeleton for analysis page
export function SkeletonAnalysisPage({ className = "" }: { className?: string }) {
  return (
    <div className={`max-w-7xl mx-auto px-4 py-8 ${className}`}>
      {/* Header */}
      <div className="mb-8">
        <Skeleton className="h-8 w-1/3 mb-2" />
        <Skeleton className="h-4 w-1/2" />
      </div>

      {/* Visibility Score Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-1">
          <SkeletonVisibilityScore />
        </div>
        <div className="lg:col-span-2">
          <SkeletonChart height={180} />
        </div>
      </div>

      {/* Provider Grid */}
      <div className="mb-8">
        <Skeleton className="h-6 w-32 mb-4" />
        <SkeletonProviderGrid count={6} />
      </div>

      {/* Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <SkeletonInsightCard />
        <SkeletonInsightCard />
      </div>

      {/* Recommendations */}
      <div>
        <Skeleton className="h-6 w-40 mb-4" />
        <SkeletonRecommendationsList count={3} />
      </div>
    </div>
  );
}

// Full page loading skeleton for dashboard
export function SkeletonDashboard({ className = "" }: { className?: string }) {
  return (
    <div className={`max-w-7xl mx-auto px-4 py-8 ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-64" />
        </div>
        <Skeleton className="h-10 w-32 rounded-lg" />
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>

      {/* Analysis list */}
      <div>
        <Skeleton className="h-6 w-40 mb-4" />
        <SkeletonAnalysisList count={5} />
      </div>
    </div>
  );
}

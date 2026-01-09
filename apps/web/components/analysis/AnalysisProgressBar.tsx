/**
 * Analysis Progress Bar
 *
 * Shows overall progress of provider queries (enabled providers only).
 */
"use client";

interface AnalysisProgressBarProps {
  completed: number;
  total: number;
  enabledProvidersCount: number;
  isComplete?: boolean;
}

export default function AnalysisProgressBar({
  completed,
  total,
  enabledProvidersCount,
  isComplete = false,
}: AnalysisProgressBarProps) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  return (
    <div className="w-full">
      {/* Progress stats */}
      <div className="mb-2 flex items-center justify-between text-sm">
        <div className="flex items-center space-x-2">
          <span className="font-medium text-gray-700">
            Overall Progress
          </span>
          <span className="text-gray-500">
            ({enabledProvidersCount} {enabledProvidersCount === 1 ? "provider" : "providers"} enabled)
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-gray-900">
            {completed} / {total}
          </span>
          <span className="text-gray-600">({percentage}%)</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className={`h-full transition-all duration-500 ease-out ${
            isComplete
              ? "bg-green-500"
              : percentage > 0
              ? "bg-blue-600"
              : "bg-gray-300"
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Status message */}
      <div className="mt-2 text-center text-sm">
        {isComplete ? (
          <span className="font-medium text-green-700">
            ✅ Analysis complete! All providers finished.
          </span>
        ) : completed === 0 ? (
          <span className="text-gray-600">
            ⏳ Waiting for providers to start...
          </span>
        ) : (
          <span className="text-blue-700">
            🔄 Querying providers... ({total - completed} remaining)
          </span>
        )}
      </div>
    </div>
  );
}

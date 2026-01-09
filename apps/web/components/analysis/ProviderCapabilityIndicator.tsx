/**
 * Provider Capability Indicator Component
 *
 * Shows provider capabilities (citations/no-citations, success/failure).
 */
"use client";

interface ProviderCapabilityIndicatorProps {
  hasCitations: boolean;
  hasSuccess: boolean;
  citationCount?: number;
}

export default function ProviderCapabilityIndicator({
  hasCitations,
  hasSuccess,
  citationCount = 0,
}: ProviderCapabilityIndicatorProps) {
  return (
    <div className="flex items-center space-x-3">
      {/* Success/Failure Indicator */}
      <div className="flex items-center space-x-1">
        {hasSuccess ? (
          <>
            <span className="text-green-600">✓</span>
            <span className="text-sm font-medium text-green-700">Success</span>
          </>
        ) : (
          <>
            <span className="text-red-600">✗</span>
            <span className="text-sm font-medium text-red-700">Failed</span>
          </>
        )}
      </div>

      {/* Citation Capability */}
      {hasSuccess && (
        <div
          className={`flex items-center space-x-1 rounded-full px-3 py-1 text-sm font-medium ${
            hasCitations
              ? "bg-blue-100 text-blue-800"
              : "bg-gray-100 text-gray-600"
          }`}
        >
          {hasCitations ? (
            <>
              <span>📎</span>
              <span>
                {citationCount} {citationCount === 1 ? "Citation" : "Citations"}
              </span>
            </>
          ) : (
            <>
              <span>○</span>
              <span>No Citations</span>
            </>
          )}
        </div>
      )}
    </div>
  );
}

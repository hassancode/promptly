/**
 * Provider Status Card
 *
 * Displays the status of a single AI provider query.
 */
"use client";

import { useState } from "react";

export type ProviderStatus = "pending" | "in_progress" | "completed" | "failed" | "timeout";

export interface ProviderCardData {
  provider: string;
  status: ProviderStatus;
  model?: string;
  hasCitations?: boolean;
  citationCount?: number;
  error?: string;
  responseId?: string;
  enabled: boolean;
}

interface ProviderStatusCardProps {
  data: ProviderCardData;
  onRetry?: (provider: string, responseId: string) => void;
}

const providerNames: Record<string, string> = {
  openai: "OpenAI",
  claude: "Claude",
  gemini: "Gemini",
  perplexity: "Perplexity",
  google_ai: "Google AI",
  huggingface: "Hugging Face",
};

const providerIcons: Record<string, string> = {
  openai: "🤖",
  claude: "🧠",
  gemini: "💎",
  perplexity: "🔍",
  google_ai: "🌐",
  huggingface: "🤗",
};

export default function ProviderStatusCard({
  data,
  onRetry,
}: ProviderStatusCardProps) {
  const [isRetrying, setIsRetrying] = useState(false);

  const displayName = providerNames[data.provider] || data.provider;
  const icon = providerIcons[data.provider] || "⚡";

  const handleRetry = async () => {
    if (!data.responseId || !onRetry) return;

    setIsRetrying(true);
    try {
      await onRetry(data.provider, data.responseId);
    } finally {
      setIsRetrying(false);
    }
  };

  // Status styling
  const getStatusStyles = () => {
    if (!data.enabled) {
      return {
        border: "border-gray-300",
        bg: "bg-gray-50",
        text: "text-gray-500",
        badge: "bg-gray-200 text-gray-600",
      };
    }

    switch (data.status) {
      case "completed":
        return {
          border: "border-green-300",
          bg: "bg-green-50",
          text: "text-green-900",
          badge: "bg-green-200 text-green-800",
        };
      case "failed":
      case "timeout":
        return {
          border: "border-red-300",
          bg: "bg-red-50",
          text: "text-red-900",
          badge: "bg-red-200 text-red-800",
        };
      case "in_progress":
        return {
          border: "border-blue-300",
          bg: "bg-blue-50",
          text: "text-blue-900",
          badge: "bg-blue-200 text-blue-800",
        };
      default:
        return {
          border: "border-gray-300",
          bg: "bg-white",
          text: "text-gray-900",
          badge: "bg-gray-200 text-gray-700",
        };
    }
  };

  const styles = getStatusStyles();

  // Status icon
  const getStatusIcon = () => {
    if (!data.enabled) return "⚪";

    switch (data.status) {
      case "completed":
        return "✅";
      case "failed":
        return "❌";
      case "timeout":
        return "⏱️";
      case "in_progress":
        return "🔄";
      default:
        return "⏳";
    }
  };

  // Status text
  const getStatusText = () => {
    if (!data.enabled) return "Disabled";

    switch (data.status) {
      case "completed":
        return "Completed";
      case "failed":
        return "Failed";
      case "timeout":
        return "Timeout";
      case "in_progress":
        return "In Progress";
      default:
        return "Pending";
    }
  };

  return (
    <div
      className={`rounded-lg border-2 p-4 transition-all ${styles.border} ${styles.bg}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{icon}</span>
          <div>
            <h3 className={`font-semibold ${styles.text}`}>{displayName}</h3>
            {data.model && (
              <p className="text-xs text-gray-600 mt-0.5">{data.model}</p>
            )}
          </div>
        </div>

        {/* Status Badge */}
        <span
          className={`inline-flex items-center space-x-1 rounded-full px-2.5 py-1 text-xs font-medium ${styles.badge}`}
        >
          <span>{getStatusIcon()}</span>
          <span>{getStatusText()}</span>
        </span>
      </div>

      {/* Progress indicator for in-progress */}
      {data.status === "in_progress" && data.enabled && (
        <div className="mt-3">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-blue-200">
            <div className="h-full animate-pulse bg-blue-600" style={{ width: "60%" }}></div>
          </div>
          <p className="mt-1 text-xs text-gray-600">Querying provider...</p>
        </div>
      )}

      {/* Success details */}
      {data.status === "completed" && data.enabled && (
        <div className="mt-3 flex items-center space-x-4 text-sm">
          {data.hasCitations && (
            <div className="flex items-center space-x-1 text-green-700">
              <span>📎</span>
              <span>{data.citationCount || 0} citations</span>
            </div>
          )}
          {!data.hasCitations && (
            <div className="text-gray-600">No citations</div>
          )}
        </div>
      )}

      {/* Error details */}
      {(data.status === "failed" || data.status === "timeout") && data.enabled && (
        <div className="mt-3">
          {data.error && (
            <p className="text-sm text-red-700 mb-2">{data.error}</p>
          )}

          {/* Retry button */}
          {onRetry && data.responseId && (
            <button
              onClick={handleRetry}
              disabled={isRetrying}
              className="inline-flex items-center space-x-2 rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>🔄</span>
              <span>{isRetrying ? "Retrying..." : "Retry"}</span>
            </button>
          )}
        </div>
      )}

      {/* Disabled message */}
      {!data.enabled && (
        <p className="mt-2 text-xs text-gray-500">
          Provider not enabled in configuration
        </p>
      )}
    </div>
  );
}

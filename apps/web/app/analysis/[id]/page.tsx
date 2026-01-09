/**
 * Analysis Progress Page
 *
 * Real-time analysis progress tracking with SSE streaming.
 * Displays provider statuses, responses, and overall progress as they arrive.
 */
"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useSSE } from "@/lib/use-sse";
import ProviderStatusCard, {
  ProviderCardData,
  ProviderStatus,
} from "@/components/analysis/ProviderStatusCard";
import AnalysisProgressBar from "@/components/analysis/AnalysisProgressBar";
import ResponseList from "@/components/analysis/ResponseList";

interface Citation {
  id: string;
  url: string;
  title?: string;
  snippet?: string;
  position: number;
}

interface AIResponse {
  id: string;
  provider: string;
  model_name: string;
  answer_text: {
    text: string;
    structured_data?: any;
  };
  citation_coverage: string;
  citations: Citation[];
  created_at: string;
}

interface AnalysisData {
  id: string;
  brand_name: string;
  competitors: string[];
  prompts: string[];
  location?: string;
  status: string;
  enabled_providers: string[];
}

export default function AnalysisProgressPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = params.id as string;

  // State for provider statuses
  const [providers, setProviders] = useState<Record<string, ProviderCardData>>(
    {}
  );

  // State for responses
  const [responses, setResponses] = useState<AIResponse[]>([]);

  // State for overall progress
  const [progress, setProgress] = useState({
    completed: 0,
    total: 0,
    enabledProvidersCount: 0,
    isComplete: false,
  });

  // State for analysis data
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(true);

  // Fetch analysis data on mount
  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await fetch(`/api/v1/analyses/${analysisId}`, {
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error("Failed to fetch analysis");
        }

        const data = await response.json();
        setAnalysisData(data);

        // Initialize provider cards
        const initialProviders: Record<string, ProviderCardData> = {};
        const allProviders = [
          "openai",
          "claude",
          "gemini",
          "perplexity",
          "google_ai",
          "huggingface",
        ];

        allProviders.forEach((provider) => {
          initialProviders[provider] = {
            provider,
            status: "pending",
            enabled: data.enabled_providers.includes(provider),
          };
        });

        setProviders(initialProviders);
        setProgress({
          completed: 0,
          total: data.enabled_providers.length,
          enabledProvidersCount: data.enabled_providers.length,
          isComplete: false,
        });
      } catch (error) {
        console.error("Failed to fetch analysis:", error);
      } finally {
        setIsLoadingAnalysis(false);
      }
    };

    fetchAnalysis();
  }, [analysisId]);

  // SSE event handler
  const handleSSEEvent = (event: { event: string; data: any }) => {
    console.log("SSE Event:", event.event, event.data);

    switch (event.event) {
      case "provider_started":
        setProviders((prev) => ({
          ...prev,
          [event.data.provider]: {
            ...prev[event.data.provider],
            status: "in_progress" as ProviderStatus,
            model: event.data.model,
          },
        }));
        break;

      case "provider_completed":
        setProviders((prev) => ({
          ...prev,
          [event.data.provider]: {
            ...prev[event.data.provider],
            status: "completed" as ProviderStatus,
            hasCitations: event.data.citation_count > 0,
            citationCount: event.data.citation_count,
            responseId: event.data.response_id,
          },
        }));

        // Fetch and add the new response
        if (event.data.response_id) {
          fetchResponse(event.data.response_id);
        }
        break;

      case "provider_failed":
        setProviders((prev) => ({
          ...prev,
          [event.data.provider]: {
            ...prev[event.data.provider],
            status: event.data.reason === "timeout" ? "timeout" : "failed",
            error: event.data.error,
            responseId: event.data.response_id,
          },
        }));
        break;

      case "progress_update":
        setProgress((prev) => ({
          ...prev,
          completed: event.data.completed,
          total: event.data.total,
        }));
        break;

      case "analysis_complete":
        setProgress((prev) => ({
          ...prev,
          isComplete: true,
        }));
        break;

      case "error":
        console.error("SSE Error:", event.data.message);
        break;
    }
  };

  // Fetch individual response
  const fetchResponse = async (responseId: string) => {
    try {
      const response = await fetch(
        `/api/v1/analyses/${analysisId}/responses?response_id=${responseId}`,
        {
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch response");
      }

      const data = await response.json();
      if (data.responses && data.responses.length > 0) {
        setResponses((prev) => {
          // Avoid duplicates
          const exists = prev.some((r) => r.id === data.responses[0].id);
          if (exists) return prev;
          return [...prev, data.responses[0]];
        });
      }
    } catch (error) {
      console.error("Failed to fetch response:", error);
    }
  };

  // Retry handler
  const handleRetry = async (provider: string, responseId: string) => {
    try {
      const response = await fetch(
        `/api/v1/analyses/${analysisId}/responses/${responseId}/retry`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Retry failed");
      }

      // Update provider status to in_progress
      setProviders((prev) => ({
        ...prev,
        [provider]: {
          ...prev[provider],
          status: "in_progress" as ProviderStatus,
          error: undefined,
        },
      }));
    } catch (error) {
      console.error("Retry failed:", error);
      alert("Failed to retry provider. Please try again.");
    }
  };

  // Connect to SSE stream
  const { isConnected, error: sseError } = useSSE(
    analysisData ? `/api/v1/analyses/${analysisId}/stream` : null,
    {
      onEvent: handleSSEEvent,
      onError: (error) => {
        console.error("SSE Connection Error:", error);
      },
      onOpen: () => {
        console.log("SSE Connection Opened");
      },
      onClose: () => {
        console.log("SSE Connection Closed");
      },
    }
  );

  if (isLoadingAnalysis) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-7xl">
          <div className="animate-pulse space-y-8">
            <div className="h-8 w-64 rounded bg-gray-200"></div>
            <div className="h-4 w-96 rounded bg-gray-200"></div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 rounded-lg bg-gray-200"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-lg border border-red-200 bg-red-50 p-8 text-center">
            <p className="text-lg text-red-700">Analysis not found</p>
            <button
              onClick={() => router.push("/dashboard")}
              className="mt-4 rounded-md bg-red-600 px-4 py-2 text-white hover:bg-red-700"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Header */}
        <div>
          <div className="mb-2 flex items-center space-x-3">
            <button
              onClick={() => router.push("/dashboard")}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back to Dashboard
            </button>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">
            Analysis: {analysisData.brand_name}
          </h1>
          <p className="mt-2 text-gray-600">
            Comparing against: {analysisData.competitors.join(", ")}
          </p>
          {analysisData.location && (
            <p className="mt-1 text-sm text-gray-500">
              📍 Location: {analysisData.location}
            </p>
          )}
        </div>

        {/* SSE Connection Status */}
        {!isConnected && !progress.isComplete && (
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
            <p className="text-sm text-yellow-800">
              ⚠️ Not connected to real-time stream. Reconnecting...
            </p>
          </div>
        )}

        {sseError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4">
            <p className="text-sm text-red-800">
              ❌ Connection error: {sseError.message}
            </p>
          </div>
        )}

        {/* Overall Progress */}
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <AnalysisProgressBar
            completed={progress.completed}
            total={progress.total}
            enabledProvidersCount={progress.enabledProvidersCount}
            isComplete={progress.isComplete}
          />
        </div>

        {/* Provider Status Cards */}
        <div>
          <h2 className="mb-4 text-xl font-semibold text-gray-900">
            Provider Status
          </h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.values(providers).map((provider) => (
              <ProviderStatusCard
                key={provider.provider}
                data={provider}
                onRetry={handleRetry}
              />
            ))}
          </div>
        </div>

        {/* Responses */}
        <div>
          <h2 className="mb-4 text-xl font-semibold text-gray-900">
            AI Responses
            {responses.length > 0 && (
              <span className="ml-2 text-base font-normal text-gray-600">
                ({responses.length})
              </span>
            )}
          </h2>
          <ResponseList
            responses={responses}
            isLoading={!progress.isComplete && responses.length === 0}
          />
        </div>

        {/* Completion Actions */}
        {progress.isComplete && (
          <div className="rounded-lg border border-green-200 bg-green-50 p-6 text-center">
            <p className="mb-4 text-lg font-semibold text-green-900">
              ✅ Analysis Complete!
            </p>
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => router.push(`/insights/${analysisId}`)}
                className="rounded-md bg-green-600 px-6 py-2 font-medium text-white hover:bg-green-700"
              >
                View Insights →
              </button>
              <button
                onClick={() => router.push("/dashboard")}
                className="rounded-md border border-gray-300 bg-white px-6 py-2 font-medium text-gray-700 hover:bg-gray-50"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

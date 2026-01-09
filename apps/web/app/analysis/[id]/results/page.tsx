/**
 * Analysis Results Page
 *
 * Displays collected AI responses organized by provider and prompt,
 * with citations, confidence levels, and comparison capabilities.
 */
"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import ResponseViewer from "@/components/analysis/ResponseViewer";
import ProviderComparison from "@/components/analysis/ProviderComparison";

interface Citation {
  id: string;
  url: string;
  title?: string;
  snippet?: string;
  source_type: string;
  validity_status: string;
  position: number;
  created_at: string;
}

interface AIResponse {
  id: string;
  prompt_id: string;
  provider: string;
  model_name: string;
  answer_text: {
    text: string;
    structured_data?: any;
  };
  citation_coverage: string;
  status: string;
  created_at: string;
  completed_at?: string;
  citations: Citation[];
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

export default function AnalysisResultsPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = params.id as string;

  const [responses, setResponses] = useState<AIResponse[]>([]);
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<"provider" | "comparison">("provider");

  // Fetch analysis and responses
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);

      try {
        // Fetch analysis data
        const analysisResponse = await fetch(`/api/v1/analyses/${analysisId}`, {
          credentials: "include",
        });

        if (!analysisResponse.ok) {
          throw new Error("Failed to fetch analysis");
        }

        const analysis = await analysisResponse.json();
        setAnalysisData(analysis);

        // Fetch all responses
        const responsesResponse = await fetch(
          `/api/v1/analyses/${analysisId}/responses`,
          {
            credentials: "include",
          }
        );

        if (!responsesResponse.ok) {
          throw new Error("Failed to fetch responses");
        }

        const responsesData = await responsesResponse.json();
        setResponses(responsesData);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [analysisId]);

  const handleGetInsights = () => {
    router.push(`/analysis/${analysisId}/insights`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-7xl">
          <div className="animate-pulse space-y-8">
            <div className="h-8 w-64 rounded bg-gray-200"></div>
            <div className="h-4 w-96 rounded bg-gray-200"></div>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 rounded-lg bg-gray-200"></div>
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

  // Calculate response statistics
  const totalResponses = responses.length;
  const successfulResponses = responses.filter((r) => r.status === "completed").length;
  const totalCitations = responses.reduce(
    (sum, r) => sum + (r.citations?.length || 0),
    0
  );
  const avgCitationsPerResponse =
    successfulResponses > 0 ? (totalCitations / successfulResponses).toFixed(1) : "0";

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Header */}
        <div>
          <div className="mb-2 flex items-center space-x-3">
            <button
              onClick={() => router.push(`/analysis/${analysisId}`)}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back to Progress
            </button>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">
            Analysis Results: {analysisData.brand_name}
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

        {/* Statistics Summary */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-gray-600">Total Responses</p>
            <p className="mt-2 text-3xl font-bold text-gray-900">{totalResponses}</p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-gray-600">Successful</p>
            <p className="mt-2 text-3xl font-bold text-green-600">
              {successfulResponses}
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-gray-600">Total Citations</p>
            <p className="mt-2 text-3xl font-bold text-blue-600">{totalCitations}</p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-gray-600">Avg Citations</p>
            <p className="mt-2 text-3xl font-bold text-purple-600">
              {avgCitationsPerResponse}
            </p>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center justify-between">
          <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1 shadow-sm">
            <button
              onClick={() => setViewMode("provider")}
              className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                viewMode === "provider"
                  ? "bg-blue-600 text-white"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              By Provider
            </button>
            <button
              onClick={() => setViewMode("comparison")}
              className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                viewMode === "comparison"
                  ? "bg-blue-600 text-white"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Side-by-Side
            </button>
          </div>

          {/* Get Insights Button */}
          <button
            onClick={handleGetInsights}
            className="inline-flex items-center space-x-2 rounded-md bg-green-600 px-6 py-3 font-semibold text-white shadow-sm hover:bg-green-700"
          >
            <span>🔍</span>
            <span>Get Insights</span>
            <span>→</span>
          </button>
        </div>

        {/* Response Viewer / Comparison */}
        {viewMode === "provider" ? (
          <ResponseViewer responses={responses} />
        ) : (
          <ProviderComparison responses={responses} />
        )}

        {/* Empty State */}
        {responses.length === 0 && (
          <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
            <p className="text-xl font-semibold text-gray-900">
              No responses available yet
            </p>
            <p className="mt-2 text-gray-600">
              Responses will appear here once providers have been queried.
            </p>
            <button
              onClick={() => router.push(`/analysis/${analysisId}`)}
              className="mt-6 rounded-md bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
            >
              Back to Progress
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Provider Comparison Component
 *
 * Side-by-side comparison of provider responses for the same prompt.
 */
"use client";

import { useState } from "react";
import ConfidenceBadge from "./ConfidenceBadge";
import CitationCard from "./CitationCard";

interface Citation {
  id: string;
  url: string;
  title?: string;
  snippet?: string;
  source_type: string;
  validity_status: string;
  position: number;
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

interface ProviderComparisonProps {
  responses: AIResponse[];
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

export default function ProviderComparison({ responses }: ProviderComparisonProps) {
  const [selectedPromptId, setSelectedPromptId] = useState<string | null>(null);

  // Group responses by prompt_id
  const groupedByPrompt = responses.reduce((acc, response) => {
    if (!acc[response.prompt_id]) {
      acc[response.prompt_id] = [];
    }
    acc[response.prompt_id].push(response);
    return acc;
  }, {} as Record<string, AIResponse[]>);

  // Get unique prompt IDs
  const promptIds = Object.keys(groupedByPrompt);

  // Auto-select first prompt if none selected
  const activePromptId = selectedPromptId || promptIds[0] || null;
  const promptResponses = activePromptId ? groupedByPrompt[activePromptId] : [];

  const calculateConfidence = (response: AIResponse): string => {
    const citationCount = response.citations?.length || 0;
    const coverage = response.citation_coverage;

    if (citationCount >= 3 && coverage === "complete") {
      return "high";
    } else if (citationCount >= 1 || coverage === "partial") {
      return "medium";
    } else {
      return "low";
    }
  };

  if (promptIds.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
        <p className="text-gray-600">No responses available for comparison</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Prompt Selector */}
      {promptIds.length > 1 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Select Prompt to Compare
          </label>
          <select
            value={activePromptId || ""}
            onChange={(e) => setSelectedPromptId(e.target.value)}
            className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {promptIds.map((promptId, index) => (
              <option key={promptId} value={promptId}>
                Prompt {index + 1} ({groupedByPrompt[promptId].length} responses)
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Side-by-Side Comparison Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {promptResponses.map((response) => {
          const displayName = providerNames[response.provider] || response.provider;
          const icon = providerIcons[response.provider] || "⚡";
          const confidence = calculateConfidence(response);
          const answerText = response.answer_text?.text || "";

          return (
            <div
              key={response.id}
              className="flex flex-col rounded-lg border-2 border-gray-200 bg-white shadow-sm"
            >
              {/* Provider Header */}
              <div className="border-b border-gray-200 bg-gray-50 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{icon}</span>
                    <div>
                      <h3 className="font-bold text-gray-900">{displayName}</h3>
                      <p className="text-xs text-gray-600">{response.model_name}</p>
                    </div>
                  </div>
                  <ConfidenceBadge level={confidence} />
                </div>
              </div>

              {/* Response Content */}
              <div className="flex-1 p-4">
                {response.status === "completed" ? (
                  <>
                    {/* Answer */}
                    <div className="prose prose-sm max-w-none">
                      <div className="whitespace-pre-wrap text-gray-800 line-clamp-6">
                        {answerText}
                      </div>
                    </div>

                    {/* Citation Summary */}
                    <div className="mt-4 flex items-center space-x-4 border-t border-gray-200 pt-4">
                      <div className="flex items-center space-x-2 text-sm">
                        <span className="font-medium text-gray-700">Citations:</span>
                        <span className="font-semibold text-blue-600">
                          {response.citations.length}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm">
                        <span className="font-medium text-gray-700">Coverage:</span>
                        <span
                          className={`font-semibold capitalize ${
                            response.citation_coverage === "complete"
                              ? "text-green-600"
                              : response.citation_coverage === "partial"
                              ? "text-yellow-600"
                              : "text-gray-600"
                          }`}
                        >
                          {response.citation_coverage}
                        </span>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="rounded-md bg-red-50 p-4">
                    <p className="text-sm text-red-700">
                      Response {response.status}: Unable to retrieve answer
                    </p>
                  </div>
                )}
              </div>

              {/* Citations List (Collapsible) */}
              {response.status === "completed" && response.citations.length > 0 && (
                <details className="border-t border-gray-200">
                  <summary className="cursor-pointer bg-gray-50 p-4 text-sm font-medium text-gray-700 hover:bg-gray-100">
                    View {response.citations.length} Citations
                  </summary>
                  <div className="space-y-2 p-4">
                    {response.citations.map((citation) => (
                      <CitationCard key={citation.id} citation={citation} />
                    ))}
                  </div>
                </details>
              )}
            </div>
          );
        })}
      </div>

      {/* Comparison Summary */}
      <div className="rounded-lg border border-gray-200 bg-blue-50 p-6">
        <h3 className="mb-4 text-lg font-semibold text-blue-900">
          Comparison Summary
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <p className="text-sm font-medium text-blue-700">Total Providers</p>
            <p className="mt-1 text-2xl font-bold text-blue-900">
              {promptResponses.length}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-blue-700">Total Citations</p>
            <p className="mt-1 text-2xl font-bold text-blue-900">
              {promptResponses.reduce((sum, r) => sum + r.citations.length, 0)}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-blue-700">Avg Confidence</p>
            <p className="mt-1 text-2xl font-bold text-blue-900">
              {promptResponses.length > 0
                ? (
                    promptResponses.filter(
                      (r) => calculateConfidence(r) === "high"
                    ).length / promptResponses.length
                  ).toFixed(1)
                : "N/A"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

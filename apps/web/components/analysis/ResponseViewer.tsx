/**
 * Response Viewer Component
 *
 * Displays AI responses organized by provider, with citations and confidence levels.
 */
"use client";

import { useState } from "react";
import CitationCard from "./CitationCard";
import ConfidenceBadge from "./ConfidenceBadge";
import ProviderCapabilityIndicator from "./ProviderCapabilityIndicator";
import CitationModal from "./CitationModal";

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

interface ResponseViewerProps {
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

export default function ResponseViewer({ responses }: ResponseViewerProps) {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [expandedResponses, setExpandedResponses] = useState<Set<string>>(new Set());

  // Group responses by provider
  const groupedResponses = responses.reduce((acc, response) => {
    if (!acc[response.provider]) {
      acc[response.provider] = [];
    }
    acc[response.provider].push(response);
    return acc;
  }, {} as Record<string, AIResponse[]>);

  const toggleExpand = (responseId: string) => {
    setExpandedResponses((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(responseId)) {
        newSet.delete(responseId);
      } else {
        newSet.add(responseId);
      }
      return newSet;
    });
  };

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

  return (
    <div className="space-y-8">
      {Object.entries(groupedResponses).map(([provider, providerResponses]) => {
        const displayName = providerNames[provider] || provider;
        const icon = providerIcons[provider] || "⚡";
        const successfulResponses = providerResponses.filter(
          (r) => r.status === "completed"
        );
        const hasSuccess = successfulResponses.length > 0;

        return (
          <div key={provider} className="space-y-4">
            {/* Provider Header */}
            <div className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex items-center space-x-3">
                <span className="text-3xl">{icon}</span>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{displayName}</h3>
                  <p className="text-sm text-gray-600">
                    {successfulResponses.length} of {providerResponses.length} successful
                  </p>
                </div>
              </div>
              <ProviderCapabilityIndicator
                hasCitations={successfulResponses.some((r) => r.citations.length > 0)}
                hasSuccess={hasSuccess}
                citationCount={successfulResponses.reduce(
                  (sum, r) => sum + r.citations.length,
                  0
                )}
              />
            </div>

            {/* Provider Responses */}
            {providerResponses.map((response) => {
              const isExpanded = expandedResponses.has(response.id);
              const confidence = calculateConfidence(response);
              const answerText = response.answer_text?.text || "";
              const truncatedText =
                answerText.length > 300 && !isExpanded
                  ? answerText.substring(0, 300) + "..."
                  : answerText;

              return (
                <div
                  key={response.id}
                  className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
                >
                  {/* Response Header */}
                  <div className="mb-4 flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-700">
                          {response.model_name}
                        </span>
                        <span className="text-sm text-gray-500">
                          •
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(response.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <ConfidenceBadge level={confidence} />
                  </div>

                  {/* Answer Text */}
                  {response.status === "completed" ? (
                    <>
                      <div className="prose prose-sm max-w-none">
                        <div className="whitespace-pre-wrap text-gray-800">
                          {truncatedText}
                        </div>
                      </div>

                      {answerText.length > 300 && (
                        <button
                          onClick={() => toggleExpand(response.id)}
                          className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-800"
                        >
                          {isExpanded ? "Show less" : "Show more"}
                        </button>
                      )}

                      {/* Citations */}
                      {response.citations.length > 0 && (
                        <div className="mt-6 border-t border-gray-200 pt-4">
                          <h4 className="mb-3 text-sm font-semibold text-gray-700">
                            Citations ({response.citations.length})
                          </h4>
                          <div className="space-y-3">
                            {response.citations.map((citation) => (
                              <CitationCard
                                key={citation.id}
                                citation={citation}
                                onViewDetails={() => setSelectedCitation(citation)}
                              />
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="rounded-md bg-red-50 p-4">
                      <p className="text-sm text-red-700">
                        Response {response.status}: Unable to retrieve answer
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        );
      })}

      {/* Citation Modal */}
      {selectedCitation && (
        <CitationModal
          citation={selectedCitation}
          onClose={() => setSelectedCitation(null)}
        />
      )}
    </div>
  );
}

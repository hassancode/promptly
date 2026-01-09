"use client";

/**
 * Evidence Drill-Down Modal Component
 *
 * Task: T189 [US6]
 * Shows linked AI responses and citations for an insight or recommendation
 */

import { useState, useEffect } from "react";

interface Citation {
  id: string;
  url: string;
  title: string;
  snippet?: string;
  source_type: string;
  validity_status: "valid" | "broken" | "unknown";
  position: number;
}

interface AIResponse {
  id: string;
  provider: string;
  model_name: string;
  answer_text: string;
  citations: Citation[];
  status: "success" | "failed" | "timeout";
  created_at: string;
}

interface EvidenceReference {
  ai_response_id: string;
  citation_id?: string;
  relevance_score?: number;
}

interface EvidenceModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  evidenceReferences: EvidenceReference[];
  aiResponses: AIResponse[];
}

export default function EvidenceModal({
  isOpen,
  onClose,
  title,
  description,
  evidenceReferences,
  aiResponses,
}: EvidenceModalProps) {
  const [activeTab, setActiveTab] = useState<"responses" | "citations">("responses");

  // Filter responses based on evidence references
  const linkedResponses = aiResponses.filter((response) =>
    evidenceReferences.some((ref) => ref.ai_response_id === response.id)
  );

  // Collect all citations from linked responses
  const linkedCitations = linkedResponses.flatMap((response) =>
    response.citations.map((citation) => ({
      ...citation,
      provider: response.provider,
    }))
  );

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "unset";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="mx-4 max-w-4xl w-full max-h-[90vh] rounded-xl bg-white shadow-2xl flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
              {description && (
                <p className="mt-1 text-sm text-gray-600">{description}</p>
              )}
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close modal"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Tabs */}
          <div className="mt-4 flex gap-4 border-b border-gray-200">
            <button
              onClick={() => setActiveTab("responses")}
              className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "responses"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              AI Responses ({linkedResponses.length})
            </button>
            <button
              onClick={() => setActiveTab("citations")}
              className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "citations"
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              Citations ({linkedCitations.length})
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === "responses" ? (
            <ResponsesTab responses={linkedResponses} />
          ) : (
            <CitationsTab citations={linkedCitations} />
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 flex justify-end flex-shrink-0">
          <button
            onClick={onClose}
            className="px-6 py-2 text-gray-700 hover:text-gray-900 font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function ResponsesTab({ responses }: { responses: AIResponse[] }) {
  if (responses.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No AI responses linked to this insight.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {responses.map((response) => (
        <div
          key={response.id}
          className="p-4 rounded-lg border border-gray-200 bg-gray-50"
        >
          {/* Provider Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <ProviderBadge provider={response.provider} />
              <span className="text-sm text-gray-500">{response.model_name}</span>
            </div>
            <StatusBadge status={response.status} />
          </div>

          {/* Response Text */}
          <div className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
            {response.answer_text}
          </div>

          {/* Citations Summary */}
          {response.citations.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-500 mb-2">
                {response.citations.length} citation(s) from this response
              </p>
              <div className="flex flex-wrap gap-2">
                {response.citations.slice(0, 3).map((citation, index) => (
                  <a
                    key={citation.id || index}
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-2 py-1 bg-white border border-gray-200 rounded text-xs text-blue-600 hover:text-blue-700 hover:border-blue-300 transition-colors"
                  >
                    <svg
                      className="w-3 h-3 mr-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                      />
                    </svg>
                    {citation.title || new URL(citation.url).hostname}
                  </a>
                ))}
                {response.citations.length > 3 && (
                  <span className="text-xs text-gray-400">
                    +{response.citations.length - 3} more
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function CitationsTab({
  citations,
}: {
  citations: (Citation & { provider: string })[];
}) {
  if (citations.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No citations available for this insight.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {citations.map((citation, index) => (
        <div
          key={citation.id || index}
          className="p-4 rounded-lg border border-gray-200 bg-white"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {/* Title */}
              <a
                href={citation.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                {citation.title || "Untitled Source"}
              </a>

              {/* URL */}
              <p className="text-xs text-gray-500 mt-1 truncate max-w-xl">
                {citation.url}
              </p>

              {/* Snippet */}
              {citation.snippet && (
                <p className="text-sm text-gray-600 mt-2 line-clamp-3">
                  {citation.snippet}
                </p>
              )}
            </div>

            {/* Validity Badge */}
            <ValidityBadge status={citation.validity_status} />
          </div>

          {/* Source Info */}
          <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
            <span>Source: {citation.source_type}</span>
            <span>From: {citation.provider}</span>
            <span>Position: #{citation.position + 1}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function ProviderBadge({ provider }: { provider: string }) {
  const providerColors: Record<string, string> = {
    openai: "bg-green-100 text-green-700",
    claude: "bg-orange-100 text-orange-700",
    gemini: "bg-blue-100 text-blue-700",
    perplexity: "bg-purple-100 text-purple-700",
    google_ai: "bg-red-100 text-red-700",
    huggingface: "bg-yellow-100 text-yellow-700",
  };

  return (
    <span
      className={`px-2 py-1 rounded text-xs font-medium ${
        providerColors[provider.toLowerCase()] || "bg-gray-100 text-gray-700"
      }`}
    >
      {provider}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const statusStyles: Record<string, string> = {
    success: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
    timeout: "bg-yellow-100 text-yellow-700",
  };

  return (
    <span
      className={`px-2 py-1 rounded text-xs font-medium ${
        statusStyles[status] || "bg-gray-100 text-gray-700"
      }`}
    >
      {status}
    </span>
  );
}

function ValidityBadge({ status }: { status: string }) {
  const validityStyles: Record<string, { bg: string; icon: string }> = {
    valid: { bg: "text-green-600", icon: "M5 13l4 4L19 7" },
    broken: { bg: "text-red-600", icon: "M6 18L18 6M6 6l12 12" },
    unknown: { bg: "text-gray-400", icon: "M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
  };

  const style = validityStyles[status] || validityStyles.unknown;

  return (
    <div className={`flex items-center ${style.bg}`}>
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d={style.icon}
        />
      </svg>
    </div>
  );
}

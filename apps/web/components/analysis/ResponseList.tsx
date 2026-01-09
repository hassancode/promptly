/**
 * Response List
 *
 * Displays AI provider responses as they arrive, with citations.
 */
"use client";

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

interface ResponseListProps {
  responses: AIResponse[];
  isLoading?: boolean;
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

export default function ResponseList({
  responses,
  isLoading = false,
}: ResponseListProps) {
  if (isLoading && responses.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
        <div className="animate-pulse">
          <div className="mx-auto h-12 w-12 rounded-full bg-gray-200"></div>
          <p className="mt-4 text-gray-600">Waiting for responses...</p>
        </div>
      </div>
    );
  }

  if (responses.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center">
        <p className="text-gray-600">No responses yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {responses.map((response) => (
        <ResponseCard key={response.id} response={response} />
      ))}
    </div>
  );
}

function ResponseCard({ response }: { response: AIResponse }) {
  const displayName = providerNames[response.provider] || response.provider;
  const icon = providerIcons[response.provider] || "⚡";

  // Extract text from answer
  const answerText = response.answer_text?.text || "";

  // Coverage badge color
  const getCoverageColor = () => {
    switch (response.citation_coverage) {
      case "complete":
        return "bg-green-100 text-green-800";
      case "partial":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      {/* Header */}
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{icon}</span>
          <div>
            <h3 className="font-semibold text-gray-900">{displayName}</h3>
            <p className="text-xs text-gray-500">{response.model_name}</p>
          </div>
        </div>

        {/* Citation coverage badge */}
        <span
          className={`rounded-full px-3 py-1 text-xs font-medium ${getCoverageColor()}`}
        >
          {response.citation_coverage === "complete" && "📎 Complete citations"}
          {response.citation_coverage === "partial" && "📎 Some citations"}
          {response.citation_coverage === "none" && "No citations"}
        </span>
      </div>

      {/* Answer text */}
      <div className="prose prose-sm max-w-none">
        <div className="whitespace-pre-wrap text-gray-800">{answerText}</div>
      </div>

      {/* Citations */}
      {response.citations.length > 0 && (
        <div className="mt-4 border-t border-gray-200 pt-4">
          <h4 className="mb-2 text-sm font-semibold text-gray-700">
            Citations ({response.citations.length})
          </h4>
          <div className="space-y-2">
            {response.citations.map((citation, index) => (
              <div
                key={citation.id}
                className="rounded-md bg-gray-50 p-3 text-sm"
              >
                <div className="flex items-start space-x-2">
                  <span className="flex-shrink-0 font-medium text-gray-500">
                    [{index + 1}]
                  </span>
                  <div className="flex-1">
                    {citation.title && (
                      <p className="font-medium text-gray-900">
                        {citation.title}
                      </p>
                    )}
                    {citation.snippet && (
                      <p className="mt-1 text-gray-600">{citation.snippet}</p>
                    )}
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800"
                    >
                      <span className="break-all">{citation.url}</span>
                      <span className="flex-shrink-0">↗</span>
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

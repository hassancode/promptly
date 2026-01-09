/**
 * Citation Card Component
 *
 * Displays citation information with URL, title, snippet, and validity badge.
 */
"use client";

interface Citation {
  id: string;
  url: string;
  title?: string;
  snippet?: string;
  source_type: string;
  validity_status: string;
  position: number;
}

interface CitationCardProps {
  citation: Citation;
  onViewDetails?: () => void;
}

const validityColors: Record<string, string> = {
  valid: "bg-green-100 text-green-800",
  broken: "bg-red-100 text-red-800",
  suspicious: "bg-yellow-100 text-yellow-800",
  unknown: "bg-gray-100 text-gray-800",
};

const validityIcons: Record<string, string> = {
  valid: "✓",
  broken: "✗",
  suspicious: "⚠",
  unknown: "?",
};

const sourceTypeIcons: Record<string, string> = {
  academic: "🎓",
  news: "📰",
  official: "🏢",
  social: "💬",
  other: "🔗",
};

export default function CitationCard({ citation, onViewDetails }: CitationCardProps) {
  const validityColor = validityColors[citation.validity_status] || validityColors.unknown;
  const validityIcon = validityIcons[citation.validity_status] || validityIcons.unknown;
  const sourceIcon = sourceTypeIcons[citation.source_type] || sourceTypeIcons.other;

  // Extract domain from URL
  const getDomain = (url: string): string => {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch {
      return url;
    }
  };

  return (
    <div className="group rounded-md border border-gray-200 bg-gray-50 p-4 transition-colors hover:bg-gray-100">
      <div className="flex items-start space-x-3">
        {/* Position Badge */}
        <div className="flex-shrink-0">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-800">
            {citation.position}
          </span>
        </div>

        {/* Content */}
        <div className="flex-1 space-y-2">
          {/* Title */}
          {citation.title && (
            <h5 className="font-semibold text-gray-900">{citation.title}</h5>
          )}

          {/* Snippet */}
          {citation.snippet && (
            <p className="text-sm text-gray-600 line-clamp-2">{citation.snippet}</p>
          )}

          {/* URL and Badges */}
          <div className="flex flex-wrap items-center gap-2">
            {/* URL */}
            <a
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800"
              onClick={(e) => e.stopPropagation()}
            >
              <span className="break-all">{getDomain(citation.url)}</span>
              <span className="flex-shrink-0">↗</span>
            </a>

            {/* Source Type Badge */}
            <span className="inline-flex items-center space-x-1 rounded-full bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-700">
              <span>{sourceIcon}</span>
              <span className="capitalize">{citation.source_type}</span>
            </span>

            {/* Validity Badge */}
            <span
              className={`inline-flex items-center space-x-1 rounded-full px-2 py-0.5 text-xs font-medium ${validityColor}`}
            >
              <span>{validityIcon}</span>
              <span className="capitalize">{citation.validity_status}</span>
            </span>
          </div>

          {/* View Details Button */}
          {onViewDetails && (
            <button
              onClick={onViewDetails}
              className="mt-2 text-sm font-medium text-gray-600 hover:text-gray-900 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              View Details →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

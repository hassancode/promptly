/**
 * Citation Modal Component
 *
 * Modal displaying full citation details.
 */
"use client";

import { useEffect } from "react";

interface Citation {
  id: string;
  url: string;
  title?: string;
  snippet?: string;
  source_type: string;
  validity_status: string;
  position: number;
  created_at?: string;
}

interface CitationModalProps {
  citation: Citation;
  onClose: () => void;
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

const sourceTypeLabels: Record<string, string> = {
  academic: "Academic Source",
  news: "News Article",
  official: "Official/Company Website",
  social: "Social Media",
  other: "Other Source",
};

export default function CitationModal({ citation, onClose }: CitationModalProps) {
  // Close on ESC key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "unset";
    };
  }, []);

  const validityColor = validityColors[citation.validity_status] || validityColors.unknown;
  const validityIcon = validityIcons[citation.validity_status] || validityIcons.unknown;
  const sourceLabel = sourceTypeLabels[citation.source_type] || "Other Source";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl rounded-lg bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b border-gray-200 p-6">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900">Citation Details</h2>
            <p className="mt-1 text-sm text-gray-600">Reference #{citation.position}</p>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="Close modal"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
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

        {/* Content */}
        <div className="max-h-[60vh] space-y-6 overflow-y-auto p-6">
          {/* Title */}
          {citation.title && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Title</label>
              <p className="mt-1 text-lg font-semibold text-gray-900">
                {citation.title}
              </p>
            </div>
          )}

          {/* URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700">URL</label>
            <a
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 inline-flex items-center space-x-2 break-all text-blue-600 hover:text-blue-800"
            >
              <span>{citation.url}</span>
              <span className="flex-shrink-0">↗</span>
            </a>
          </div>

          {/* Snippet */}
          {citation.snippet && (
            <div>
              <label className="block text-sm font-medium text-gray-700">Snippet</label>
              <p className="mt-1 text-gray-800">{citation.snippet}</p>
            </div>
          )}

          {/* Metadata Grid */}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {/* Source Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Source Type
              </label>
              <div className="mt-1 inline-flex items-center space-x-2 rounded-md bg-gray-100 px-3 py-2">
                <span className="capitalize text-gray-900">{sourceLabel}</span>
              </div>
            </div>

            {/* Validity Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Validity Status
              </label>
              <div className="mt-1">
                <span
                  className={`inline-flex items-center space-x-1 rounded-md px-3 py-2 text-sm font-medium ${validityColor}`}
                >
                  <span>{validityIcon}</span>
                  <span className="capitalize">{citation.validity_status}</span>
                </span>
              </div>
            </div>

            {/* Position */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Position in Response
              </label>
              <p className="mt-1 text-gray-900">#{citation.position}</p>
            </div>

            {/* Created At */}
            {citation.created_at && (
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Retrieved At
                </label>
                <p className="mt-1 text-gray-900">
                  {new Date(citation.created_at).toLocaleString()}
                </p>
              </div>
            )}
          </div>

          {/* Validity Status Description */}
          <div className="rounded-md bg-blue-50 p-4">
            <h4 className="text-sm font-semibold text-blue-900">
              About Validity Status
            </h4>
            <p className="mt-2 text-sm text-blue-800">
              {citation.validity_status === "valid" &&
                "This URL was verified as accessible and returned a valid response."}
              {citation.validity_status === "broken" &&
                "This URL could not be accessed or returned an error. It may be broken or unavailable."}
              {citation.validity_status === "suspicious" &&
                "This URL has patterns that may indicate it is suspicious or unreliable (e.g., URL shortener, IP address)."}
              {citation.validity_status === "unknown" &&
                "This URL has not been validated yet or validation was inconclusive."}
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 border-t border-gray-200 p-6">
          <button
            onClick={onClose}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-gray-700 hover:bg-gray-50"
          >
            Close
          </button>
          <a
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-2 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            <span>Visit Source</span>
            <span>↗</span>
          </a>
        </div>
      </div>
    </div>
  );
}

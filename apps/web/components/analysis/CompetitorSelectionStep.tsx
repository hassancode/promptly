"use client";

/**
 * Competitor Selection Step Component
 *
 * Second step in the analysis wizard where user:
 * - Reviews AI-suggested competitors
 * - Adds custom competitors
 * - Confirms final competitor list (max 5)
 */
import { useState, useEffect } from "react";
import {
  Analysis,
  Competitor,
  CompetitorSuggestion,
  suggestCompetitors,
  addCompetitor,
} from "@/lib/analysis-api";
import { validateCompetitorName } from "@/lib/form-validation";

const MAX_COMPETITORS = 5;

interface CompetitorSelectionStepProps {
  analysis: Analysis;
  onComplete: () => void;
  onBack: () => void;
}

export default function CompetitorSelectionStep({
  analysis,
  onComplete,
  onBack,
}: CompetitorSelectionStepProps) {
  const [suggestions, setSuggestions] = useState<CompetitorSuggestion[]>([]);
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [customInput, setCustomInput] = useState("");
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(true);
  const [isAddingCompetitor, setIsAddingCompetitor] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inputError, setInputError] = useState<string | null>(null);

  // Load AI suggestions on mount
  useEffect(() => {
    loadSuggestions();
  }, [analysis.id]);

  const loadSuggestions = async () => {
    setIsLoadingSuggestions(true);
    setError(null);

    try {
      const response = await suggestCompetitors(analysis.id);
      setSuggestions(response.competitors);
    } catch (err: any) {
      setError("Failed to load competitor suggestions");
      console.error("Failed to load suggestions:", err);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  const handleAddCompetitor = async (competitorName: string) => {
    // Validate
    const validationError = validateCompetitorName(competitorName);
    if (validationError) {
      setInputError(validationError);
      return;
    }

    // Check limit
    if (competitors.length >= MAX_COMPETITORS) {
      setInputError(`Maximum ${MAX_COMPETITORS} competitors allowed`);
      return;
    }

    // Check duplicate (case-insensitive)
    const isDuplicate = competitors.some(
      (c) => c.name.toLowerCase() === competitorName.trim().toLowerCase()
    );
    if (isDuplicate) {
      setInputError("This competitor has already been added");
      return;
    }

    setIsAddingCompetitor(true);
    setError(null);
    setInputError(null);

    try {
      const newCompetitor = await addCompetitor(analysis.id, {
        competitor_name: competitorName.trim(),
      });

      // Add to list
      setCompetitors([...competitors, newCompetitor]);

      // Clear input
      setCustomInput("");
    } catch (err: any) {
      setError(err.message || "Failed to add competitor");
    } finally {
      setIsAddingCompetitor(false);
    }
  };

  const handleAddFromSuggestion = (suggestion: CompetitorSuggestion) => {
    handleAddCompetitor(suggestion.name);
  };

  const handleAddCustom = (e: React.FormEvent) => {
    e.preventDefault();
    handleAddCompetitor(customInput);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomInput(e.target.value);
    if (inputError) setInputError(null);
  };

  const canAddMore = competitors.length < MAX_COMPETITORS;
  const hasMinimumCompetitors = competitors.length >= 1;

  return (
    <div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-2">
        Select Competitors
      </h2>
      <p className="text-gray-600 mb-8">
        We'll compare {analysis.brand_name} against these competitors in
        AI-generated answers.
      </p>

      {/* Error Display */}
      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* AI Suggestions */}
      <div className="mb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          AI-Suggested Competitors
        </h3>

        {isLoadingSuggestions ? (
          <div className="space-y-3">
            <CompetitorSkeleton />
            <CompetitorSkeleton />
            <CompetitorSkeleton />
          </div>
        ) : suggestions.length > 0 ? (
          <div className="space-y-3">
            {suggestions.map((suggestion, index) => {
              const isAdded = competitors.some(
                (c) =>
                  c.name.toLowerCase() === suggestion.name.toLowerCase()
              );

              return (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 rounded-lg border border-gray-200 bg-gray-50"
                >
                  <div className="flex items-center">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600 font-semibold mr-3">
                      {suggestion.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {suggestion.name}
                      </p>
                      <p className="text-sm text-gray-500">AI Suggestion</p>
                    </div>
                  </div>

                  {isAdded ? (
                    <span className="px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-lg">
                      Added
                    </span>
                  ) : (
                    <button
                      onClick={() => handleAddFromSuggestion(suggestion)}
                      disabled={!canAddMore || isAddingCompetitor}
                      className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {canAddMore ? "Add" : "Limit Reached"}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">
            No suggestions available. Add competitors manually below.
          </p>
        )}
      </div>

      {/* Custom Competitor Input */}
      <div className="mb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Add Custom Competitor
        </h3>

        <form onSubmit={handleAddCustom} className="flex gap-3">
          <div className="flex-1">
            <input
              type="text"
              value={customInput}
              onChange={handleInputChange}
              placeholder="Enter competitor name..."
              disabled={!canAddMore || isAddingCompetitor}
              className={`w-full rounded-lg border px-4 py-3 focus:outline-none focus:ring-2 ${
                inputError
                  ? "border-red-300 focus:border-red-500 focus:ring-red-200"
                  : "border-gray-300 focus:border-blue-500 focus:ring-blue-200"
              } ${
                !canAddMore || isAddingCompetitor
                  ? "bg-gray-100 cursor-not-allowed"
                  : ""
              }`}
            />
            {inputError && (
              <p className="mt-2 text-sm text-red-600">{inputError}</p>
            )}
          </div>
          <button
            type="submit"
            disabled={!canAddMore || !customInput.trim() || isAddingCompetitor}
            className="px-6 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isAddingCompetitor ? "Adding..." : "Add"}
          </button>
        </form>
      </div>

      {/* Added Competitors List */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Selected Competitors ({competitors.length}/{MAX_COMPETITORS})
          </h3>
        </div>

        {competitors.length > 0 ? (
          <div className="space-y-2">
            {competitors.map((competitor) => (
              <div
                key={competitor.id}
                className="flex items-center p-3 rounded-lg border border-green-200 bg-green-50"
              >
                <svg
                  className="h-5 w-5 text-green-600 mr-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <span className="font-medium text-gray-900">
                  {competitor.name}
                </span>
                {competitor.is_suggested && (
                  <span className="ml-2 text-xs text-gray-500">
                    (AI Suggested)
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
            <p className="text-gray-500">
              No competitors selected yet. Add at least one to continue.
            </p>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-6 border-t">
        <button
          type="button"
          onClick={onBack}
          className="px-6 py-3 text-gray-700 hover:text-gray-900"
        >
          Back
        </button>
        <button
          onClick={onComplete}
          disabled={!hasMinimumCompetitors}
          className="px-8 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Continue to Dashboard
        </button>
      </div>
    </div>
  );
}

function CompetitorSkeleton() {
  return (
    <div className="flex items-center justify-between p-4 rounded-lg border border-gray-200 bg-gray-50 animate-pulse">
      <div className="flex items-center">
        <div className="h-10 w-10 rounded-full bg-gray-200 mr-3" />
        <div>
          <div className="h-4 w-32 bg-gray-200 rounded mb-2" />
          <div className="h-3 w-24 bg-gray-200 rounded" />
        </div>
      </div>
      <div className="h-9 w-16 bg-gray-200 rounded-lg" />
    </div>
  );
}

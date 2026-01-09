"use client";

/**
 * Prompt Selection Step Component
 *
 * Third step in the analysis wizard where user:
 * - Reviews AI-suggested prompts
 * - Adds custom prompts
 * - Confirms final prompt list (max 7)
 */
import { useState, useEffect } from "react";
import {
  Analysis,
  Prompt,
  PromptSuggestion,
  suggestPrompts,
  addPrompt,
} from "@/lib/analysis-api";
import { validatePromptText } from "@/lib/form-validation";

const MAX_PROMPTS = 7;
const MAX_PROMPT_CHARS = 500;

interface PromptSelectionStepProps {
  analysis: Analysis;
  onComplete: () => void;
  onBack: () => void;
}

export default function PromptSelectionStep({
  analysis,
  onComplete,
  onBack,
}: PromptSelectionStepProps) {
  const [suggestions, setSuggestions] = useState<PromptSuggestion[]>([]);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [customInput, setCustomInput] = useState("");
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(true);
  const [isAddingPrompt, setIsAddingPrompt] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inputError, setInputError] = useState<string | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  // Load AI suggestions on mount
  useEffect(() => {
    loadSuggestions();
  }, [analysis.id]);

  const loadSuggestions = async () => {
    setIsLoadingSuggestions(true);
    setError(null);

    try {
      const response = await suggestPrompts(analysis.id);
      setSuggestions(response.prompts);
    } catch (err: any) {
      setError("Failed to load prompt suggestions");
      console.error("Failed to load suggestions:", err);
    } finally {
      setIsLoadingSuggestions(false);
    }
  };

  const handleAddPrompt = async (promptText: string) => {
    // Validate
    const validationError = validatePromptText(promptText);
    if (validationError) {
      setInputError(validationError);
      return;
    }

    // Check character limit
    if (promptText.length > MAX_PROMPT_CHARS) {
      setInputError(`Maximum ${MAX_PROMPT_CHARS} characters allowed`);
      return;
    }

    // Check limit
    if (prompts.length >= MAX_PROMPTS) {
      setInputError(`Maximum ${MAX_PROMPTS} prompts allowed`);
      return;
    }

    // Check duplicate (case-insensitive)
    const isDuplicate = prompts.some(
      (p) => p.text.toLowerCase() === promptText.trim().toLowerCase()
    );
    if (isDuplicate) {
      setInputError("This prompt has already been added");
      return;
    }

    setIsAddingPrompt(true);
    setError(null);
    setInputError(null);

    try {
      const newPrompt = await addPrompt(analysis.id, {
        prompt_text: promptText.trim(),
      });

      // Add to list
      setPrompts([...prompts, newPrompt]);

      // Clear input
      setCustomInput("");
    } catch (err: any) {
      setError(err.message || "Failed to add prompt");
    } finally {
      setIsAddingPrompt(false);
    }
  };

  const handleAddFromSuggestion = (suggestion: PromptSuggestion) => {
    handleAddPrompt(suggestion.text);
  };

  const handleAddCustom = (e: React.FormEvent) => {
    e.preventDefault();
    handleAddPrompt(customInput);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCustomInput(e.target.value);
    if (inputError) setInputError(null);
  };

  const canAddMore = prompts.length < MAX_PROMPTS;
  const hasMinimumPrompts = prompts.length >= 1;

  return (
    <div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-2">
        Select Prompts
      </h2>
      <p className="text-gray-600 mb-8">
        Choose questions that AI assistants will answer to compare your brand
        visibility.
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
          AI-Suggested Prompts
        </h3>

        {isLoadingSuggestions ? (
          <div className="space-y-3">
            <PromptSkeleton />
            <PromptSkeleton />
            <PromptSkeleton />
            <PromptSkeleton />
            <PromptSkeleton />
          </div>
        ) : suggestions.length > 0 ? (
          <div className="space-y-3">
            {suggestions.map((suggestion, index) => {
              const isAdded = prompts.some(
                (p) => p.text.toLowerCase() === suggestion.text.toLowerCase()
              );

              return (
                <div
                  key={index}
                  className="flex items-start justify-between p-4 rounded-lg border border-gray-200 bg-gray-50"
                >
                  <div className="flex items-start flex-1">
                    <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600 font-semibold mr-3 mt-1">
                      {index + 1}
                    </div>
                    <p className="text-gray-900 leading-relaxed">
                      {suggestion.text}
                    </p>
                  </div>

                  {isAdded ? (
                    <span className="ml-4 px-4 py-2 text-sm font-medium text-green-700 bg-green-100 rounded-lg whitespace-nowrap">
                      Added
                    </span>
                  ) : (
                    <button
                      onClick={() => handleAddFromSuggestion(suggestion)}
                      disabled={!canAddMore || isAddingPrompt}
                      className="ml-4 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
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
            No suggestions available. Add prompts manually below.
          </p>
        )}
      </div>

      {/* Custom Prompt Input */}
      <div className="mb-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Add Custom Prompt
        </h3>

        <form onSubmit={handleAddCustom}>
          <div className="mb-3">
            <textarea
              value={customInput}
              onChange={handleInputChange}
              placeholder="Enter a question you'd like AI assistants to answer..."
              rows={3}
              disabled={!canAddMore || isAddingPrompt}
              className={`w-full rounded-lg border px-4 py-3 focus:outline-none focus:ring-2 resize-none ${
                inputError
                  ? "border-red-300 focus:border-red-500 focus:ring-red-200"
                  : "border-gray-300 focus:border-blue-500 focus:ring-blue-200"
              } ${
                !canAddMore || isAddingPrompt
                  ? "bg-gray-100 cursor-not-allowed"
                  : ""
              }`}
            />
            <div className="flex justify-between mt-2">
              <div>
                {inputError && (
                  <p className="text-sm text-red-600">{inputError}</p>
                )}
                {!inputError && (
                  <p className="text-sm text-gray-500">
                    Example: "What are the best electric vehicles for families?"
                  </p>
                )}
              </div>
              <span className={`text-sm ${customInput.length > MAX_PROMPT_CHARS ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
                {customInput.length}/{MAX_PROMPT_CHARS}
              </span>
            </div>
          </div>
          <button
            type="submit"
            disabled={!canAddMore || !customInput.trim() || isAddingPrompt}
            className="w-full px-6 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isAddingPrompt ? "Adding..." : "Add Custom Prompt"}
          </button>
        </form>
      </div>

      {/* Added Prompts List */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Selected Prompts ({prompts.length}/{MAX_PROMPTS})
          </h3>
        </div>

        {prompts.length > 0 ? (
          <div className="space-y-2">
            {prompts.map((prompt, index) => (
              <div
                key={prompt.id}
                className="flex items-start p-3 rounded-lg border border-green-200 bg-green-50"
              >
                <svg
                  className="h-5 w-5 text-green-600 mr-3 mt-0.5 flex-shrink-0"
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
                <div className="flex-1">
                  <p className="text-gray-900">{prompt.text}</p>
                  {prompt.is_suggested && (
                    <span className="text-xs text-gray-500">
                      (AI Suggested)
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
            <p className="text-gray-500">
              No prompts selected yet. Add at least one to continue.
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
          onClick={() => setShowConfirmModal(true)}
          disabled={!hasMinimumPrompts}
          className="px-8 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Start Analysis
        </button>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <StartAnalysisConfirmModal
          analysis={analysis}
          prompts={prompts}
          onConfirm={() => {
            setShowConfirmModal(false);
            onComplete();
          }}
          onCancel={() => setShowConfirmModal(false)}
        />
      )}
    </div>
  );
}

interface StartAnalysisConfirmModalProps {
  analysis: Analysis;
  prompts: Prompt[];
  onConfirm: () => void;
  onCancel: () => void;
}

function StartAnalysisConfirmModal({
  analysis,
  prompts,
  onConfirm,
  onCancel,
}: StartAnalysisConfirmModalProps) {
  // Mock enabled providers - in production, this would come from API
  const enabledProviders = [
    { name: "OpenAI", enabled: true },
    { name: "Claude", enabled: true },
    { name: "Gemini", enabled: true },
    { name: "Perplexity", enabled: true },
    { name: "Google AI", enabled: true },
    { name: "Hugging Face", enabled: true },
  ].filter(p => p.enabled);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="mx-4 max-w-lg w-full rounded-xl bg-white shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900">
            Start Analysis
          </h3>
          <p className="mt-1 text-sm text-gray-600">
            Review your analysis configuration before starting
          </p>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 max-h-[60vh] overflow-y-auto">
          {/* Brand Info */}
          <div>
            <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
              Brand
            </h4>
            <p className="mt-1 text-lg font-medium text-gray-900">
              {analysis.brand_name}
            </p>
          </div>

          {/* Location */}
          <div>
            <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
              Location
            </h4>
            <p className="mt-1 text-gray-900">
              {analysis.location || "Auto-detected based on your IP"}
            </p>
          </div>

          {/* Competitors */}
          {analysis.competitors && analysis.competitors.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                Competitors ({analysis.competitors.length})
              </h4>
              <div className="mt-2 flex flex-wrap gap-2">
                {analysis.competitors.map((comp, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {comp.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Prompts */}
          <div>
            <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
              Prompts ({prompts.length})
            </h4>
            <ul className="mt-2 space-y-2">
              {prompts.map((prompt, index) => (
                <li key={prompt.id} className="flex items-start">
                  <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center bg-blue-100 text-blue-600 rounded-full text-xs font-medium mr-2">
                    {index + 1}
                  </span>
                  <span className="text-gray-700 text-sm">{prompt.text}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Enabled Providers */}
          <div>
            <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
              AI Providers ({enabledProviders.length})
            </h4>
            <div className="mt-2 flex flex-wrap gap-2">
              {enabledProviders.map((provider) => (
                <span
                  key={provider.name}
                  className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm flex items-center"
                >
                  <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {provider.name}
                </span>
              ))}
            </div>
          </div>

          {/* Time Estimate */}
          <div className="rounded-lg bg-blue-50 p-4">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-blue-600 mr-3 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm font-medium text-blue-900">
                  Estimated time: 10-30 seconds
                </p>
                <p className="text-sm text-blue-700">
                  Results will stream in as each provider responds
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="px-6 py-2 text-gray-700 hover:text-gray-900 font-medium"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Start Analysis
          </button>
        </div>
      </div>
    </div>
  );
}

function PromptSkeleton() {
  return (
    <div className="flex items-start justify-between p-4 rounded-lg border border-gray-200 bg-gray-50 animate-pulse">
      <div className="flex items-start flex-1">
        <div className="h-8 w-8 rounded-full bg-gray-200 mr-3" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full" />
          <div className="h-4 bg-gray-200 rounded w-3/4" />
        </div>
      </div>
      <div className="ml-4 h-9 w-16 bg-gray-200 rounded-lg" />
    </div>
  );
}

"use client";

/**
 * Brand Entry Step Component
 *
 * First step in the analysis wizard where user enters their brand name.
 */
import { useState } from "react";
import { validateBrandName } from "@/lib/form-validation";

interface BrandEntryStepProps {
  onSubmit: (brandName: string) => void;
  isLoading?: boolean;
}

export default function BrandEntryStep({
  onSubmit,
  isLoading = false,
}: BrandEntryStepProps) {
  const [brandName, setBrandName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate brand name
    const validationError = validateBrandName(brandName);
    if (validationError) {
      setError(validationError);
      return;
    }

    // Clear error and submit
    setError(null);
    onSubmit(brandName.trim());
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBrandName(e.target.value);
    // Clear error on change
    if (error) setError(null);
  };

  return (
    <div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-2">
        Enter Your Brand Name
      </h2>
      <p className="text-gray-600 mb-8">
        We'll analyze how your brand appears in AI-generated answers compared to
        competitors.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="mb-6">
          <label
            htmlFor="brand-name"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Brand Name
          </label>
          <input
            id="brand-name"
            type="text"
            value={brandName}
            onChange={handleChange}
            placeholder="e.g., Tesla, Apple, Nike"
            disabled={isLoading}
            className={`w-full rounded-lg border px-4 py-3 focus:outline-none focus:ring-2 ${
              error
                ? "border-red-300 focus:border-red-500 focus:ring-red-200"
                : "border-gray-300 focus:border-blue-500 focus:ring-blue-200"
            } ${isLoading ? "bg-gray-100 cursor-not-allowed" : ""}`}
          />
          {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          <p className="mt-2 text-sm text-gray-500">
            Enter the name of your brand or company
          </p>
        </div>

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => window.history.back()}
            disabled={isLoading}
            className="px-6 py-3 text-gray-700 hover:text-gray-900 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading || !brandName.trim()}
            className="px-8 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <span className="flex items-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Creating...
              </span>
            ) : (
              "Next: Select Competitors"
            )}
          </button>
        </div>
      </form>

      {/* Info Box */}
      <div className="mt-8 rounded-lg bg-blue-50 border border-blue-200 p-4">
        <div className="flex">
          <svg
            className="h-5 w-5 text-blue-600 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-900">
              What happens next?
            </h3>
            <div className="mt-2 text-sm text-blue-800">
              <ul className="list-disc list-inside space-y-1">
                <li>We'll suggest 3 relevant competitors using AI</li>
                <li>You can add up to 2 additional custom competitors</li>
                <li>Then we'll query multiple AI systems to compare visibility</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

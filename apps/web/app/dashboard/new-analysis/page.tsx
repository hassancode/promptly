"use client";

/**
 * New Analysis Wizard
 *
 * Multi-step wizard for creating a brand analysis:
 * 1. Enter brand name
 * 2. Select/add competitors (AI suggestions + custom)
 * 3. Review and start analysis
 */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/lib/protected-route";
import BrandEntryStep from "@/components/analysis/BrandEntryStep";
import CompetitorSelectionStep from "@/components/analysis/CompetitorSelectionStep";
import PromptSelectionStep from "@/components/analysis/PromptSelectionStep";
import { createAnalysis } from "@/lib/analysis-api";
import { Analysis } from "@/lib/analysis-api";

type WizardStep = "brand" | "competitors" | "prompts";

export default function NewAnalysisPage() {
  return (
    <ProtectedRoute>
      <NewAnalysisWizard />
    </ProtectedRoute>
  );
}

function NewAnalysisWizard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<WizardStep>("brand");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Brand entry step
  const handleBrandSubmit = async (brandName: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Create analysis
      const newAnalysis = await createAnalysis({ brand_name: brandName });
      setAnalysis(newAnalysis);

      // Move to competitor selection
      setCurrentStep("competitors");
    } catch (err: any) {
      setError(err.message || "Failed to create analysis");
    } finally {
      setIsLoading(false);
    }
  };

  // Competitor selection complete
  const handleCompetitorsComplete = () => {
    // Move to prompt selection
    setCurrentStep("prompts");
  };

  // Prompts selection complete
  const handlePromptsComplete = () => {
    // Navigate back to dashboard
    router.push("/dashboard");
  };

  // Back button
  const handleBack = () => {
    if (currentStep === "competitors") {
      setCurrentStep("brand");
    } else if (currentStep === "prompts") {
      setCurrentStep("competitors");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-4xl px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Create New Analysis
          </h1>
          <p className="mt-2 text-gray-600">
            Analyze your brand's visibility in AI-generated answers
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <Step
              number={1}
              label="Brand"
              isActive={currentStep === "brand"}
              isCompleted={
                currentStep === "competitors" || currentStep === "prompts"
              }
            />
            <div className="h-1 flex-1 bg-gray-200 mx-4">
              <div
                className={`h-full transition-all ${
                  currentStep === "competitors" || currentStep === "prompts"
                    ? "bg-blue-600 w-full"
                    : "bg-gray-200 w-0"
                }`}
              />
            </div>
            <Step
              number={2}
              label="Competitors"
              isActive={currentStep === "competitors"}
              isCompleted={currentStep === "prompts"}
            />
            <div className="h-1 flex-1 bg-gray-200 mx-4">
              <div
                className={`h-full transition-all ${
                  currentStep === "prompts" ? "bg-blue-600 w-full" : "bg-gray-200 w-0"
                }`}
              />
            </div>
            <Step number={3} label="Prompts" isActive={currentStep === "prompts"} />
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Step Content */}
        <div className="rounded-lg bg-white shadow-md p-8">
          {currentStep === "brand" && (
            <BrandEntryStep
              onSubmit={handleBrandSubmit}
              isLoading={isLoading}
            />
          )}

          {currentStep === "competitors" && analysis && (
            <CompetitorSelectionStep
              analysis={analysis}
              onComplete={handleCompetitorsComplete}
              onBack={handleBack}
            />
          )}

          {currentStep === "prompts" && analysis && (
            <PromptSelectionStep
              analysis={analysis}
              onComplete={handlePromptsComplete}
              onBack={handleBack}
            />
          )}
        </div>
      </div>
    </div>
  );
}

interface StepProps {
  number: number;
  label: string;
  isActive?: boolean;
  isCompleted?: boolean;
}

function Step({ number, label, isActive, isCompleted }: StepProps) {
  return (
    <div className="flex flex-col items-center">
      <div
        className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
          isCompleted
            ? "border-blue-600 bg-blue-600 text-white"
            : isActive
            ? "border-blue-600 bg-white text-blue-600"
            : "border-gray-300 bg-white text-gray-400"
        }`}
      >
        {isCompleted ? (
          <svg
            className="h-6 w-6"
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
        ) : (
          <span className="text-sm font-semibold">{number}</span>
        )}
      </div>
      <span
        className={`mt-2 text-sm font-medium ${
          isActive ? "text-blue-600" : "text-gray-500"
        }`}
      >
        {label}
      </span>
    </div>
  );
}

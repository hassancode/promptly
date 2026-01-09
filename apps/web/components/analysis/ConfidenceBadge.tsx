/**
 * Confidence Badge Component
 *
 * Displays confidence level with color-coded badge (High/Medium/Low).
 */
"use client";

interface ConfidenceBadgeProps {
  level: string; // "high" | "medium" | "low" | "none"
  showDescription?: boolean;
}

const confidenceColors: Record<string, string> = {
  high: "bg-green-100 text-green-800 border-green-300",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-300",
  low: "bg-orange-100 text-orange-800 border-orange-300",
  none: "bg-gray-100 text-gray-800 border-gray-300",
};

const confidenceIcons: Record<string, string> = {
  high: "✓✓✓",
  medium: "✓✓",
  low: "✓",
  none: "○",
};

const confidenceDescriptions: Record<string, string> = {
  high: "Strong evidence with multiple credible citations",
  medium: "Moderate evidence with some citations",
  low: "Limited evidence or missing citations",
  none: "No evidence or response unavailable",
};

const confidenceLabels: Record<string, string> = {
  high: "High Confidence",
  medium: "Medium Confidence",
  low: "Low Confidence",
  none: "No Confidence",
};

export default function ConfidenceBadge({
  level,
  showDescription = false,
}: ConfidenceBadgeProps) {
  const color = confidenceColors[level] || confidenceColors.none;
  const icon = confidenceIcons[level] || confidenceIcons.none;
  const label = confidenceLabels[level] || confidenceLabels.none;
  const description = confidenceDescriptions[level] || "";

  if (showDescription) {
    return (
      <div className={`rounded-lg border-2 p-4 ${color}`}>
        <div className="flex items-center space-x-2">
          <span className="text-xl">{icon}</span>
          <div>
            <p className="font-semibold">{label}</p>
            <p className="mt-1 text-sm">{description}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <span
      className={`inline-flex items-center space-x-1 rounded-full border px-3 py-1 text-sm font-medium ${color}`}
      title={description}
    >
      <span>{icon}</span>
      <span>{label}</span>
    </span>
  );
}

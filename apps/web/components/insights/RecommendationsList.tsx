'use client';

import { type Recommendation } from '@/lib/insights-api';

interface RecommendationsListProps {
  recommendations: Recommendation[];
}

export function RecommendationsList({ recommendations }: RecommendationsListProps) {
  const getImpactColor = (impact: string) => {
    switch (impact?.toLowerCase()) {
      case 'high':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getConfidenceIcon = (confidence: string) => {
    switch (confidence?.toLowerCase()) {
      case 'high':
        return '✓✓';
      case 'medium':
        return '✓';
      default:
        return '?';
    }
  };

  // Sort by priority
  const sortedRecommendations = [...recommendations].sort((a, b) => a.priority - b.priority);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Recommendations
          </h3>
          <p className="text-sm text-gray-500">
            {recommendations.length} actionable suggestions based on your insights
          </p>
        </div>
        <span className="text-2xl">💡</span>
      </div>

      <div className="space-y-4">
        {sortedRecommendations.map((rec, idx) => (
          <div
            key={rec.id}
            className={`border rounded-lg p-4 ${getImpactColor(rec.expected_impact)}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-3">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-white text-sm font-bold text-gray-700">
                  {idx + 1}
                </span>
                <span
                  className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                    rec.expected_impact === 'high'
                      ? 'bg-green-600 text-white'
                      : rec.expected_impact === 'medium'
                      ? 'bg-yellow-600 text-white'
                      : 'bg-gray-600 text-white'
                  }`}
                >
                  {rec.expected_impact} impact
                </span>
              </div>
              <span className="text-xs text-gray-500" title={`Confidence: ${rec.confidence_level}`}>
                {getConfidenceIcon(rec.confidence_level)}
              </span>
            </div>

            <h4 className="font-medium text-gray-900 mb-2">{rec.text}</h4>
            <p className="text-sm text-gray-700">{rec.rationale}</p>

            {rec.evidence_references.length > 0 && (
              <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                <span className="text-xs text-gray-600">
                  Based on {rec.evidence_references.length} insight{rec.evidence_references.length > 1 ? 's' : ''}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      {recommendations.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No recommendations available yet.
        </div>
      )}
    </div>
  );
}

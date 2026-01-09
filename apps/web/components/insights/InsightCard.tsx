'use client';

import { type Insight } from '@/lib/insights-api';

interface InsightCardProps {
  title: string;
  insight: Insight;
  icon?: string;
}

export function InsightCard({ title, insight, icon = '📈' }: InsightCardProps) {
  const getConfidenceColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'high':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Extract key metric based on insight type
  const getKeyMetric = () => {
    const scores = insight.scores as Record<string, unknown> | undefined;

    if (!scores) return null;

    switch (insight.insight_type) {
      case 'mention':
        return {
          value: scores.count as number,
          label: 'Total Mentions',
        };
      case 'visibility':
        return {
          value: `${((scores.composite as number) * 100).toFixed(0)}%`,
          label: 'Visibility',
        };
      case 'sentiment':
        return {
          value: (scores.overall as string)?.charAt(0).toUpperCase() + (scores.overall as string)?.slice(1),
          label: 'Sentiment',
        };
      default:
        return null;
    }
  };

  const metric = getKeyMetric();

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <span className="text-2xl">{icon}</span>
      </div>

      {metric && (
        <div className="text-center mb-4">
          <div className="text-3xl font-bold text-gray-900">{metric.value}</div>
          <p className="text-sm text-gray-500">{metric.label}</p>
        </div>
      )}

      <div className="flex items-center justify-between mb-3">
        <span
          className={`px-2 py-1 text-xs font-medium rounded ${getConfidenceColor(
            insight.confidence_level
          )}`}
        >
          {insight.confidence_level} confidence
        </span>
        <span className="text-xs text-gray-400">
          {insight.insight_type}
        </span>
      </div>

      <p className="text-sm text-gray-600">{insight.summary}</p>
    </div>
  );
}

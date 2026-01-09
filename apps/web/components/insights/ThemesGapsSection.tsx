'use client';

import { type Insight } from '@/lib/insights-api';

interface ThemesGapsSectionProps {
  type: 'themes' | 'gaps';
  insight: Insight;
}

interface Theme {
  name: string;
  frequency: number;
  relevance_score: number;
}

interface Gap {
  name: string;
  description: string;
  importance: string;
  recommendation: string;
}

export function ThemesGapsSection({ type, insight }: ThemesGapsSectionProps) {
  const isThemes = type === 'themes';

  const themes = (insight.scores as { themes?: Theme[] })?.themes ?? [];
  const gaps = (insight.scores as { gaps?: Gap[] })?.gaps ?? [];
  const topThemes = (insight.scores as { top_themes?: string[] })?.top_themes ?? [];

  const getImportanceColor = (importance: string) => {
    switch (importance?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {isThemes ? 'Key Themes' : 'Coverage Gaps'}
        </h3>
        <span className="text-2xl">{isThemes ? '🏷️' : '🔍'}</span>
      </div>

      {isThemes ? (
        <div className="space-y-3">
          {topThemes.length > 0 ? (
            <>
              <div className="flex flex-wrap gap-2 mb-4">
                {topThemes.map((theme, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                  >
                    {theme}
                  </span>
                ))}
              </div>
              {themes.slice(0, 5).map((theme, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                >
                  <span className="text-gray-700 capitalize">{theme.name}</span>
                  <div className="flex items-center space-x-3">
                    <span className="text-xs text-gray-500">
                      {theme.frequency} mentions
                    </span>
                    <div className="w-16 bg-gray-200 rounded-full h-1.5">
                      <div
                        className="h-1.5 rounded-full bg-blue-500"
                        style={{ width: `${theme.relevance_score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </>
          ) : (
            <p className="text-gray-500 text-sm">No themes identified</p>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {gaps.length > 0 ? (
            gaps.slice(0, 5).map((gap, idx) => (
              <div
                key={idx}
                className="p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="font-medium text-gray-900 capitalize">
                    {gap.name.replace('_', ' ')}
                  </span>
                  <span
                    className={`px-2 py-0.5 text-xs font-medium rounded ${getImportanceColor(
                      gap.importance
                    )}`}
                  >
                    {gap.importance}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{gap.description}</p>
                <p className="text-xs text-blue-600">{gap.recommendation}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-sm">No significant gaps identified</p>
          )}
        </div>
      )}

      {/* Summary */}
      <p className="mt-4 text-sm text-gray-600 border-t border-gray-100 pt-4">
        {insight.summary}
      </p>
    </div>
  );
}

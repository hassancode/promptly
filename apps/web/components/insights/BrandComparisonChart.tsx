'use client';

import { type Insight } from '@/lib/insights-api';

interface BrandComparisonChartProps {
  brandName: string;
  comparisons: Insight[];
}

export function BrandComparisonChart({ brandName, comparisons }: BrandComparisonChartProps) {
  // Extract comparison data
  const comparisonData = comparisons.map((c) => {
    const scores = c.scores as {
      brand_score?: number;
      competitor_score?: number;
      difference?: number;
    } | undefined;

    return {
      competitor: c.competitor_name ?? 'Unknown',
      brandScore: (scores?.brand_score ?? 0) * 100,
      competitorScore: (scores?.competitor_score ?? 0) * 100,
      difference: (scores?.difference ?? 0) * 100,
    };
  });

  const brandScore = comparisonData[0]?.brandScore ?? 0;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Brand vs Competitors
          </h3>
          <p className="text-sm text-gray-500">
            Visibility score comparison
          </p>
        </div>
        <span className="text-2xl">📊</span>
      </div>

      {/* Simple bar chart */}
      <div className="space-y-4">
        {/* Brand bar */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="font-medium text-gray-900">{brandName}</span>
            <span className="text-sm font-semibold text-blue-600">
              {brandScore.toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="h-4 rounded-full bg-blue-500 transition-all duration-500"
              style={{ width: `${Math.min(100, brandScore)}%` }}
            />
          </div>
        </div>

        {/* Competitor bars */}
        {comparisonData.map((data, idx) => (
          <div key={idx}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-gray-700">{data.competitor}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-semibold text-gray-600">
                  {data.competitorScore.toFixed(0)}%
                </span>
                {data.difference !== 0 && (
                  <span
                    className={`text-xs font-medium ${
                      data.difference > 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    ({data.difference > 0 ? '+' : ''}{data.difference.toFixed(0)}%)
                  </span>
                )}
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="h-4 rounded-full bg-gray-400 transition-all duration-500"
                style={{ width: `${Math.min(100, data.competitorScore)}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-blue-500" />
            <span className="text-gray-600">Your Brand</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-gray-400" />
            <span className="text-gray-600">Competitors</span>
          </div>
        </div>
      </div>
    </div>
  );
}

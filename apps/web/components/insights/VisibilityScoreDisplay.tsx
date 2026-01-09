'use client';

import { type Insight } from '@/lib/insights-api';

interface VisibilityScoreDisplayProps {
  insight: Insight;
}

export function VisibilityScoreDisplay({ insight }: VisibilityScoreDisplayProps) {
  const scores = insight.scores as {
    presence?: number;
    frequency?: number;
    position?: number;
    composite?: number;
  } | undefined;

  const composite = scores?.composite ?? 0;
  const presence = scores?.presence ?? 0;
  const frequency = scores?.frequency ?? 0;
  const position = scores?.position ?? 0;

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = (score: number) => {
    if (score >= 0.7) return 'bg-green-500';
    if (score >= 0.4) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Visibility Score</h3>
        <span className="text-2xl">👁️</span>
      </div>

      {/* Main Score */}
      <div className="text-center mb-6">
        <div className={`text-4xl font-bold ${getScoreColor(composite)}`}>
          {(composite * 100).toFixed(0)}%
        </div>
        <p className="text-sm text-gray-500">Composite Score</p>
      </div>

      {/* Score Breakdown */}
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Presence</span>
            <span className={getScoreColor(presence)}>{(presence * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressColor(presence)}`}
              style={{ width: `${presence * 100}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Frequency</span>
            <span className={getScoreColor(frequency)}>{(frequency * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressColor(frequency)}`}
              style={{ width: `${frequency * 100}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Position</span>
            <span className={getScoreColor(position)}>{(position * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressColor(position)}`}
              style={{ width: `${position * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Summary */}
      <p className="mt-4 text-sm text-gray-600">{insight.summary}</p>
    </div>
  );
}

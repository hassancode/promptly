'use client';

import { type Insight } from '@/lib/insights-api';

interface SentimentIndicatorProps {
  insight: Insight;
}

export function SentimentIndicator({ insight }: SentimentIndicatorProps) {
  const scores = insight.scores as {
    overall?: string;
    positive?: number;
    neutral?: number;
    negative?: number;
    confidence?: number;
  } | undefined;

  const overall = scores?.overall ?? 'neutral';
  const positive = scores?.positive ?? 0;
  const neutral = scores?.neutral ?? 0;
  const negative = scores?.negative ?? 0;

  const getSentimentEmoji = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😟';
      default:
        return '😐';
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'text-green-600 bg-green-50';
      case 'negative':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Sentiment</h3>
        <span className="text-2xl">{getSentimentEmoji(overall)}</span>
      </div>

      {/* Main Sentiment */}
      <div className="text-center mb-6">
        <span
          className={`inline-block px-4 py-2 rounded-full text-lg font-semibold capitalize ${getSentimentColor(
            overall
          )}`}
        >
          {overall}
        </span>
      </div>

      {/* Breakdown */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Positive</span>
          <div className="flex items-center space-x-2">
            <div className="w-24 bg-gray-200 rounded-full h-2">
              <div
                className="h-2 rounded-full bg-green-500"
                style={{ width: `${positive * 100}%` }}
              />
            </div>
            <span className="text-sm text-green-600 w-12 text-right">
              {(positive * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Neutral</span>
          <div className="flex items-center space-x-2">
            <div className="w-24 bg-gray-200 rounded-full h-2">
              <div
                className="h-2 rounded-full bg-gray-400"
                style={{ width: `${neutral * 100}%` }}
              />
            </div>
            <span className="text-sm text-gray-600 w-12 text-right">
              {(neutral * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Negative</span>
          <div className="flex items-center space-x-2">
            <div className="w-24 bg-gray-200 rounded-full h-2">
              <div
                className="h-2 rounded-full bg-red-500"
                style={{ width: `${negative * 100}%` }}
              />
            </div>
            <span className="text-sm text-red-600 w-12 text-right">
              {(negative * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* Summary */}
      <p className="mt-4 text-sm text-gray-600">{insight.summary}</p>
    </div>
  );
}

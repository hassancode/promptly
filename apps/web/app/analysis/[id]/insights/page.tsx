'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { generateInsights, getInsights, getRecommendations, type Insight, type Recommendation } from '@/lib/insights-api';
import { VisibilityScoreDisplay } from '@/components/insights/VisibilityScoreDisplay';
import { SentimentIndicator } from '@/components/insights/SentimentIndicator';
import { ThemesGapsSection } from '@/components/insights/ThemesGapsSection';
import { RecommendationsList } from '@/components/insights/RecommendationsList';
import { BrandComparisonChart } from '@/components/insights/BrandComparisonChart';
import { InsightCard } from '@/components/insights/InsightCard';

export default function InsightsPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = params.id as string;

  const [insights, setInsights] = useState<Insight[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [brandName, setBrandName] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generationTime, setGenerationTime] = useState<number | null>(null);

  const loadInsights = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [insightsData, recommendationsData] = await Promise.all([
        getInsights(analysisId),
        getRecommendations(analysisId),
      ]);

      setInsights(insightsData);
      setRecommendations(recommendationsData);

      if (insightsData.length > 0) {
        setBrandName(insightsData[0].brand_name);
      }
    } catch (err) {
      // If no insights exist yet, that's OK - we'll generate them
      console.log('No existing insights found');
    } finally {
      setLoading(false);
    }
  }, [analysisId]);

  const handleGenerateInsights = async (regenerate: boolean = false) => {
    try {
      setGenerating(true);
      setError(null);

      const result = await generateInsights(analysisId, regenerate);

      setInsights(result.insights);
      setRecommendations(result.recommendations);
      setBrandName(result.brand_name);
      setGenerationTime(result.generation_time_ms);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate insights');
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    loadInsights();
  }, [loadInsights]);

  // Auto-generate if no insights exist
  useEffect(() => {
    if (!loading && insights.length === 0 && !generating && !error) {
      handleGenerateInsights(false);
    }
  }, [loading, insights.length, generating, error]);

  // Get specific insight types
  const visibilityInsight = insights.find(i => i.insight_type === 'visibility');
  const sentimentInsight = insights.find(i => i.insight_type === 'sentiment');
  const themeInsight = insights.find(i => i.insight_type === 'theme');
  const gapInsight = insights.find(i => i.insight_type === 'gap');
  const comparisonInsights = insights.filter(i => i.insight_type === 'comparison');
  const mentionInsight = insights.find(i => i.insight_type === 'mention');

  if (loading || generating) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-lg shadow p-8">
            <div className="flex flex-col items-center justify-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="text-gray-600">
                {generating ? 'Generating insights...' : 'Loading insights...'}
              </p>
              {generating && (
                <p className="text-sm text-gray-500">
                  This typically takes less than 5 seconds
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-lg shadow p-8">
            <div className="text-center">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={() => handleGenerateInsights(false)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <Link
              href={`/analysis/${analysisId}/results`}
              className="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-block"
            >
              ← Back to Results
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">
              Insights for {brandName}
            </h1>
            {generationTime && (
              <p className="text-sm text-gray-500">
                Generated in {generationTime}ms
              </p>
            )}
          </div>
          <button
            onClick={() => handleGenerateInsights(true)}
            disabled={generating}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50"
          >
            Regenerate Insights
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {visibilityInsight && (
            <VisibilityScoreDisplay insight={visibilityInsight} />
          )}
          {sentimentInsight && (
            <SentimentIndicator insight={sentimentInsight} />
          )}
          {mentionInsight && (
            <InsightCard
              title="Mentions"
              insight={mentionInsight}
              icon="📊"
            />
          )}
        </div>

        {/* Comparison Chart */}
        {comparisonInsights.length > 0 && (
          <BrandComparisonChart
            brandName={brandName}
            comparisons={comparisonInsights}
          />
        )}

        {/* Themes and Gaps */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {themeInsight && (
            <ThemesGapsSection
              type="themes"
              insight={themeInsight}
            />
          )}
          {gapInsight && (
            <ThemesGapsSection
              type="gaps"
              insight={gapInsight}
            />
          )}
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <RecommendationsList recommendations={recommendations} />
        )}

        {/* All Insights Detail */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            All Insights ({insights.length})
          </h2>
          <div className="space-y-4">
            {insights.map((insight) => (
              <div
                key={insight.id}
                className="border border-gray-200 rounded-lg p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded mb-2">
                      {insight.insight_type}
                    </span>
                    <h3 className="font-medium text-gray-900">{insight.summary}</h3>
                    <p className="text-sm text-gray-600 mt-1 whitespace-pre-wrap">
                      {insight.explanation}
                    </p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded ${
                      insight.confidence_level === 'high'
                        ? 'bg-green-100 text-green-800'
                        : insight.confidence_level === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {insight.confidence_level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

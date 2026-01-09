/**
 * Insights API client methods
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface EvidenceReference {
  response_id?: string;
  citation_ids: string[];
  excerpt?: string;
  insight_id?: string;
}

export interface Insight {
  id: string;
  analysis_id: string;
  insight_type: 'visibility' | 'sentiment' | 'theme' | 'gap' | 'comparison' | 'mention';
  brand_name: string;
  competitor_name?: string;
  summary: string;
  explanation: string;
  evidence_references: EvidenceReference[];
  confidence_level: 'high' | 'medium' | 'low' | 'none';
  scores?: Record<string, unknown>;
  created_at: string;
}

export interface Recommendation {
  id: string;
  analysis_id: string;
  text: string;
  rationale: string;
  expected_impact: 'high' | 'medium' | 'low';
  confidence_level: 'high' | 'medium' | 'low';
  evidence_references: EvidenceReference[];
  priority: number;
  created_at: string;
}

export interface InsightsResponse {
  analysis_id: string;
  brand_name: string;
  insights: Insight[];
  recommendations: Recommendation[];
  generated_at: string;
  generation_time_ms: number;
  from_cache?: boolean;
}

export interface InsightsSummary {
  analysis_id: string;
  brand_name: string;
  total_insights: number;
  total_recommendations: number;
  visibility_score?: number;
  overall_sentiment?: string;
  insight_types: string[];
  has_insights: boolean;
}

/**
 * Generate insights for an analysis
 */
export async function generateInsights(
  analysisId: string,
  regenerate: boolean = false
): Promise<InsightsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/analyses/${analysisId}/insights/generate`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ regenerate }),
      credentials: 'include',
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to generate insights' }));
    throw new Error(error.detail || error.error || 'Failed to generate insights');
  }

  return response.json();
}

/**
 * Get existing insights for an analysis
 */
export async function getInsights(
  analysisId: string,
  insightType?: string
): Promise<Insight[]> {
  const params = new URLSearchParams();
  if (insightType) {
    params.append('insight_type', insightType);
  }

  const url = `${API_BASE_URL}/api/v1/analyses/${analysisId}/insights${
    params.toString() ? `?${params.toString()}` : ''
  }`;

  const response = await fetch(url, {
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch insights' }));
    throw new Error(error.detail || error.error || 'Failed to fetch insights');
  }

  return response.json();
}

/**
 * Get insights summary for an analysis
 */
export async function getInsightsSummary(analysisId: string): Promise<InsightsSummary> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/analyses/${analysisId}/insights/summary`,
    {
      credentials: 'include',
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch summary' }));
    throw new Error(error.detail || error.error || 'Failed to fetch insights summary');
  }

  return response.json();
}

/**
 * Get recommendations for an analysis
 */
export async function getRecommendations(
  analysisId: string,
  impactLevel?: string
): Promise<Recommendation[]> {
  const params = new URLSearchParams();
  if (impactLevel) {
    params.append('impact_level', impactLevel);
  }

  const url = `${API_BASE_URL}/api/v1/analyses/${analysisId}/insights/recommendations${
    params.toString() ? `?${params.toString()}` : ''
  }`;

  const response = await fetch(url, {
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch recommendations' }));
    throw new Error(error.detail || error.error || 'Failed to fetch recommendations');
  }

  return response.json();
}

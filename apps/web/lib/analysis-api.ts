/**
 * Analysis API Client
 *
 * Client methods for interacting with analysis endpoints.
 */
import { apiClient } from "./api-client";

// ============================================================================
// Types
// ============================================================================

export interface Analysis {
  id: string;
  brand_name: string;
  status: "draft" | "ready" | "querying" | "completed" | "failed";
  created_at: string;
}

export interface Competitor {
  id: string;
  name: string;
  is_suggested: boolean;
  created_at: string;
}

export interface CompetitorSuggestion {
  name: string;
  is_suggested: boolean;
}

export interface CreateAnalysisData {
  brand_name: string;
  context?: string;
}

export interface AddCompetitorData {
  competitor_name: string;
}

export interface CompetitorSuggestResponse {
  competitors: CompetitorSuggestion[];
}

export interface Prompt {
  id: string;
  text: string;
  is_suggested: boolean;
  created_at: string;
}

export interface PromptSuggestion {
  text: string;
  is_suggested: boolean;
}

export interface AddPromptData {
  prompt_text: string;
}

export interface PromptSuggestResponse {
  prompts: PromptSuggestion[];
}

// ============================================================================
// API Methods
// ============================================================================

/**
 * Create a new analysis
 */
export async function createAnalysis(
  data: CreateAnalysisData
): Promise<Analysis> {
  return await apiClient.post<Analysis>("/api/v1/analyses", data);
}

/**
 * Get AI competitor suggestions for an analysis
 */
export async function suggestCompetitors(
  analysisId: string
): Promise<CompetitorSuggestResponse> {
  return await apiClient.post<CompetitorSuggestResponse>(
    `/api/v1/analyses/${analysisId}/competitors/suggest`,
    {}
  );
}

/**
 * Add a competitor to an analysis
 */
export async function addCompetitor(
  analysisId: string,
  data: AddCompetitorData
): Promise<Competitor> {
  return await apiClient.post<Competitor>(
    `/api/v1/analyses/${analysisId}/competitors`,
    data
  );
}

/**
 * Get AI prompt suggestions for an analysis
 */
export async function suggestPrompts(
  analysisId: string
): Promise<PromptSuggestResponse> {
  return await apiClient.post<PromptSuggestResponse>(
    `/api/v1/analyses/${analysisId}/prompts/suggest`,
    {}
  );
}

/**
 * Add a prompt to an analysis
 */
export async function addPrompt(
  analysisId: string,
  data: AddPromptData
): Promise<Prompt> {
  return await apiClient.post<Prompt>(
    `/api/v1/analyses/${analysisId}/prompts`,
    data
  );
}

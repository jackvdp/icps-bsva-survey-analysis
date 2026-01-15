// Data loading utilities - static JSON imports

import surveyData from '@/data/survey_clean.json';
import summaryStats from '@/data/summary_stats.json';
import regionalComparison from '@/data/regional_comparison.json';
import pilotCandidates from '@/data/pilot_candidates.json';
import painPointRankings from '@/data/pain_point_rankings.json';
import infrastructureSegments from '@/data/infrastructure_segments.json';
import qualitativeSynthesis from '@/data/qualitative_synthesis.json';

import type {
  SurveyResponse,
  RegionalData,
  PilotCandidate,
  SummaryStats,
  QualitativeSynthesis,
} from './types';

// Type assertions for imported data
export const getSurveyData = (): SurveyResponse[] => surveyData as SurveyResponse[];

export const getSummaryStats = (): SummaryStats => summaryStats as unknown as SummaryStats;

export const getRegionalComparison = (): Record<string, RegionalData> =>
  regionalComparison as unknown as Record<string, RegionalData>;

export const getPilotCandidates = (): {
  all_candidates: PilotCandidate[];
  high_potential: PilotCandidate[];
  medium_potential: PilotCandidate[];
  summary: {
    total_assessed: number;
    high_potential_count: number;
    medium_potential_count: number;
    low_potential_count: number;
    top_5_candidates: { country: string; region: string; composite_score: number; suitability: string }[];
  };
  scoring_methodology: Record<string, string | Record<string, string>>;
} => pilotCandidates as ReturnType<typeof getPilotCandidates>;

export const getPainPointRankings = (): {
  area_ranking: { area: string; avg_severity: number }[];
  credential_verification: { scores: { country: string; score: number }[]; avg_score: number };
  temporary_workforce: { scores: { country: string; score: number }[]; avg_score: number };
  training_systems: { scores: { country: string; score: number }[]; avg_score: number };
  data_synchronization: { scores: { country: string; score: number }[]; avg_score: number };
  infrastructure: { scores: { country: string; score: number }[]; avg_score: number };
} => painPointRankings as ReturnType<typeof getPainPointRankings>;

export const getInfrastructureSegments = (): {
  segments: {
    advanced: { count: number; avg_score: number; countries: string[] };
    moderate: { count: number; avg_score: number; countries: string[] };
    basic: { count: number; avg_score: number; countries: string[] };
  };
  score_distribution: { mean: number; median: number; min: number; max: number };
} => infrastructureSegments as ReturnType<typeof getInfrastructureSegments>;

export const getQualitativeSynthesis = (): QualitativeSynthesis =>
  qualitativeSynthesis as QualitativeSynthesis;

// Helper functions
export const getRegionColor = (region: string): string => {
  const colors: Record<string, string> = {
    'Africa': 'hsl(var(--chart-1))',
    'Asia-Pacific': 'hsl(var(--chart-2))',
    'Europe': 'hsl(var(--chart-3))',
    'Americas': 'hsl(var(--chart-4))',
    'Other': 'hsl(var(--chart-5))',
  };
  return colors[region] || colors['Other'];
};

export const getSuitabilityColor = (suitability: string): string => {
  if (suitability === 'HIGH') return 'bg-green-500';
  if (suitability === 'MEDIUM') return 'bg-yellow-500';
  return 'bg-red-500';
};

export const formatScore = (score: number | null): string => {
  if (score === null) return 'N/A';
  return score.toFixed(1);
};

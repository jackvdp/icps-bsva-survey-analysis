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

// Helper to get top item from an object of counts
const getTopItem = (counts: Record<string, number>, excludeKeys: string[] = []): { key: string; count: number } | null => {
  const filtered = Object.entries(counts).filter(([key]) => !excludeKeys.includes(key));
  if (filtered.length === 0) return null;
  const sorted = filtered.sort(([, a], [, b]) => b - a);
  return { key: sorted[0][0], count: sorted[0][1] };
};

// Helper to get top distribution item
const getTopDistribution = (distribution: Record<string, number>): { key: string; count: number } | null => {
  const entries = Object.entries(distribution);
  if (entries.length === 0) return null;
  const sorted = entries.sort(([, a], [, b]) => b - a);
  return { key: sorted[0][0], count: sorted[0][1] };
};

// Derive key findings from the data
export interface KeyFindings {
  credentialVerification: {
    avgVerificationTime: string;
    avgVerificationTimeCount: number;
    topChallenge: string;
    topChallengeCount: number;
  };
  workforceRetention: {
    returnRate: string;
    returnRateCount: number;
    topChallenge: string;
    topChallengeCount: number;
  };
  technologyAdoption: {
    mostExplored: string;
    mostExploredCount: number;
    topBarrier: string;
    topBarrierCount: number;
  };
  topPriority: {
    theme: string;
    themeFormatted: string;
    count: number;
  };
}

export const getKeyFindings = (): KeyFindings => {
  const stats = getSummaryStats();
  const qualitative = getQualitativeSynthesis();

  // Credential Verification
  const verificationTimeTop = getTopDistribution(stats.credential_verification.verification_hours.distribution);
  const credentialChallengeTop = getTopItem(
    stats.credential_verification.challenges.option_counts,
    ['Less than 25%', 'Other', 'No significant challenges']
  );

  // Workforce Retention
  const returnRateTop = getTopDistribution(stats.workforce_retention.return_rate.distribution);
  const workforceChallengeTop = getTopItem(
    stats.temporary_workforce.challenges.option_counts,
    ['Never', 'Rarely (1-5 times per election)', 'Other']
  );

  // Technology Adoption
  const techExploredTop = getTopItem(
    stats.workforce_retention.technologies_explored.option_counts,
    ['Other']
  );
  const infraLimitationTop = getTopItem(
    stats.technology_infrastructure.limitations.option_counts,
    ['Open-Ended Response', '0-25%', 'Other']
  );

  // Top Priority Theme from qualitative
  const priorityEntries = Object.entries(qualitative.priority_themes);
  const topPriorityEntry = priorityEntries.sort(([, a], [, b]) => b - a)[0];

  // Format theme name for display
  const formatThemeName = (key: string): string => {
    const themeNames: Record<string, string> = {
      'technology_digitalization': 'Technology & Digitalization',
      'training_capacity': 'Training & Capacity Building',
      'voter_registration': 'Voter Registration',
      'funding_resources': 'Funding & Resources',
      'transparency_trust': 'Transparency & Trust',
      'security_integrity': 'Security & Integrity',
      'accessibility_inclusion': 'Accessibility & Inclusion',
      'staff_recruitment': 'Staff Recruitment',
    };
    return themeNames[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Shorten challenge names for display
  const shortenChallenge = (challenge: string): string => {
    const shortNames: Record<string, string> = {
      'Difficulty verifying in remote/offline locations': 'Remote verification',
      'Time delays in verification': 'Time delays',
      'Lack of centralised verification system': 'No central system',
      'Losing trained workers to other opportunities between elections': 'Losing trained workers',
      'No system to track worker performance across elections': 'No performance tracking',
      'No year-round engagement with temporary workers': 'No year-round engagement',
      'Biometric systems/Digital identity solutions': 'Biometrics',
      'Electronic voting systems': 'E-voting systems',
      'Budget constraints': 'Budget constraints',
      'Limited internet connectivity': 'Limited connectivity',
      'Insufficient IT support': 'Insufficient IT support',
    };
    return shortNames[challenge] || challenge;
  };

  return {
    credentialVerification: {
      avgVerificationTime: verificationTimeTop?.key || 'N/A',
      avgVerificationTimeCount: verificationTimeTop?.count || 0,
      topChallenge: shortenChallenge(credentialChallengeTop?.key || 'N/A'),
      topChallengeCount: credentialChallengeTop?.count || 0,
    },
    workforceRetention: {
      returnRate: returnRateTop?.key || 'N/A',
      returnRateCount: returnRateTop?.count || 0,
      topChallenge: shortenChallenge(workforceChallengeTop?.key || 'N/A'),
      topChallengeCount: workforceChallengeTop?.count || 0,
    },
    technologyAdoption: {
      mostExplored: shortenChallenge(techExploredTop?.key || 'N/A'),
      mostExploredCount: techExploredTop?.count || 0,
      topBarrier: shortenChallenge(infraLimitationTop?.key || 'N/A'),
      topBarrierCount: infraLimitationTop?.count || 0,
    },
    topPriority: {
      theme: topPriorityEntry?.[0] || '',
      themeFormatted: formatThemeName(topPriorityEntry?.[0] || ''),
      count: topPriorityEntry?.[1] || 0,
    },
  };
};

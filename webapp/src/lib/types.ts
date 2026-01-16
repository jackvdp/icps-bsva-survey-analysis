// Survey Data Types

export interface SurveyResponse {
  respondent_id: string;
  country: string;
  region: string;
  completion_score: number;
  fraud_incidents: number | null;
  credential_verification_hours: number | null;
  credential_challenges: string[] | null;
  temp_workforce_percentage: number | null;
  workforce_challenges: string[] | null;
  training_system_confidence: number | null;
  sync_system_confidence: number | null;
  documentation_methods: string[] | null;
  infrastructure_limitations: string[] | null;
  technologies_explored: string[] | null;
  worker_return_rate: number | null;
  worker_interest_credentials: number | null;
  followup_willing: string | null;
  temp_workers_count: string | null;
  elections_annually: string | null;
}

export interface RegionalData {
  response_count: number;
  countries: string[];
  fraud_incidents_mean: number | null;
  verification_hours_mean: number | null;
  temp_workforce_pct_mean: number | null;
  worker_return_rate_mean: number | null;
  training_confidence_mean: number | null;
  sync_confidence_mean: number | null;
  tech_recruitment_mean: number | null;
  tech_training_mean: number | null;
  tech_performance_mean: number | null;
  tech_communication_mean: number | null;
  avg_completion_score: number;
  followup_willing_count: number;
  followup_willing_pct: number;
  top_infrastructure_limitations: Record<string, number>;
  top_credential_challenges: Record<string, number>;
  technologies_explored: Record<string, number>;
}

export interface PilotCandidate {
  country: string;
  region: string;
  composite_score: number;
  need_score: number;
  capability_score: number;
  willingness_score: number;
  suitability: string;
  need_components: string[];
  capability_components: string[];
  willingness_components: string[];
  scale: {
    temp_workers_count: string | null;
    elections_annually: string | null;
  };
}

export interface PainPointArea {
  scores: { country: string; score: number }[];
  avg_score: number;
  max_score: number;
}

export interface InfrastructureSegment {
  min: number;
  max: number;
  count: number;
  avg_score: number | null;
  countries: string[];
  regions: Record<string, number>;
  respondents: {
    country: string;
    region: string;
    score: number;
    followup_willing: string | null;
  }[];
}

export interface SummaryStats {
  response_overview: {
    total_raw_responses: number;
    total_responses: number;
    date_range: { earliest: string; latest: string };
    completion: {
      mean: number;
      median: number;
      min: number;
      max: number;
    };
    countries: { unique_count: number; list: string[] };
    regions: Record<string, number>;
    followup_willing: Record<string, number>;
  };
  credential_verification: {
    fraud_incidents: {
      n: number;
      missing: number;
      mean: number;
      distribution: Record<string, number>;
    };
    verification_hours: {
      n: number;
      mean: number;
      distribution: Record<string, number>;
    };
    challenges: {
      option_counts: Record<string, number>;
    };
  };
  temporary_workforce: {
    workforce_percentage: {
      n: number;
      missing: number;
      mean: number;
      distribution: Record<string, number>;
    };
    challenges: {
      option_counts: Record<string, number>;
    };
  };
  technology_infrastructure: {
    levels: Record<string, {
      n: number;
      mean: number;
      distribution: Record<string, number>;
    }>;
    limitations: {
      option_counts: Record<string, number>;
    };
  };
  workforce_retention: {
    return_rate: {
      n: number;
      mean: number;
      distribution: Record<string, number>;
    };
    technologies_explored: {
      option_counts: Record<string, number>;
    };
  };
}

export interface QualitativeSynthesis {
  priority_themes: Record<string, number>;
  concern_themes: Record<string, number>;
  change_themes: Record<string, number>;
  compelling_quotes: {
    country: string;
    category: string;
    quote: string;
  }[];
  total_responses_analyzed: number;
}

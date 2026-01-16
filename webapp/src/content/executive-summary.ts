import { SummaryStats, QualitativeSynthesis } from '@/lib/types';

export interface ExecutiveSummaryData {
  totalResponses: number;
  uniqueCountries: number;
  regions: {
    africa: number;
    asiaPacific: number;
    europe: number;
    americas: number;
  };
  budgetConstraintsCount: number;
  budgetConstraintsPercent: number;
  technologyPriorityCount: number;
}

export function getExecutiveSummaryData(
  stats: SummaryStats,
  qualitative: QualitativeSynthesis
): ExecutiveSummaryData {
  const totalResponses = stats.response_overview.total_responses;
  const budgetConstraints = stats.technology_infrastructure.limitations.option_counts['Budget constraints'] as number;

  return {
    totalResponses,
    uniqueCountries: stats.response_overview.countries.unique_count,
    regions: {
      africa: stats.response_overview.regions.Africa,
      asiaPacific: stats.response_overview.regions['Asia-Pacific'],
      europe: stats.response_overview.regions.Europe,
      americas: stats.response_overview.regions.Americas,
    },
    budgetConstraintsCount: budgetConstraints,
    budgetConstraintsPercent: Math.round((budgetConstraints / totalResponses) * 100),
    technologyPriorityCount: qualitative.priority_themes.technology_digitalization,
  };
}

export const executiveSummaryParagraphs = [
  {
    id: 'intro',
    title: null,
    content: (data: ExecutiveSummaryData) =>
      `The ICPS Electoral Workforce Survey gathered responses from ${data.totalResponses} electoral management bodies across ${data.uniqueCountries} countries, representing a diverse cross-section of democratic institutions from Africa (${data.regions.africa} responses), Asia-Pacific (${data.regions.asiaPacific} responses), Europe (${data.regions.europe} responses), and the Americas (${data.regions.americas} responses). This problem-discovery initiative, conducted in partnership with the BSV Association, prioritised understanding the genuine operational realities facing election administrators – the day-to-day challenges of recruiting, training, credentialing, and retaining the workforce that makes democratic elections possible.`,
  },
  {
    id: 'workforce-challenge',
    title: 'The workforce challenge is universal but manifests differently across regions.',
    content: () =>
      `Election management bodies worldwide rely heavily on temporary workers – poll workers, counting staff, and election day officials who are recruited, trained, and deployed for specific electoral events. The survey reveals that the most pressing challenge is not recruiting these workers initially, but retaining institutional knowledge and trained capacity between election cycles. Over 60% of respondents cited "losing trained workers to other opportunities between elections" as a significant challenge, while many lack any systematic way to track worker performance or maintain engagement during non-election periods. This creates a costly cycle of perpetual re-recruitment and re-training.`,
  },
  {
    id: 'infrastructure',
    title: 'Infrastructure constraints vary dramatically by region.',
    content: (data: ExecutiveSummaryData) =>
      `Budget limitations emerged as the dominant barrier, cited by ${data.budgetConstraintsCount} respondents (${data.budgetConstraintsPercent}%), but the nature of constraints differs significantly. African jurisdictions face compounding challenges: limited internet connectivity affects remote credential verification, insufficient IT support hampers system maintenance, and lack of devices prevents digital record-keeping. European respondents, by contrast, reported higher confidence in their existing systems but identified resistance to change and skills gaps as primary concerns. The Americas showed mixed infrastructure maturity, with some jurisdictions managing workforces of 750,000+ temporary workers while others operate with fewer than 100.`,
  },
  {
    id: 'credential-verification',
    title: 'Credential verification presents operational friction across all contexts.',
    content: () =>
      `While most respondents reported spending fewer than 5 hours per election on credential verification, the challenges are qualitative rather than purely time-based. Difficulty verifying credentials in remote or offline locations was the top-cited challenge, followed by time delays and the lack of centralised verification systems. These issues compound in jurisdictions with large geographic spread or limited connectivity, where a worker's training history and credentials may exist only in paper records at a distant regional office.`,
  },
  {
    id: 'training-systems',
    title: 'Training systems show moderate confidence but fragile foundations.',
    content: () =>
      `Respondents expressed generally high confidence in their training delivery systems, with 24 of 29 reporting they feel "confident" in their training record accuracy. However, when probed about how they handle lost or disputed training records, responses revealed heavy reliance on manual fallbacks: paper backup records, supervisor judgment calls, or simply excluding workers from deployment. This suggests that confidence may be based on low incident rates rather than robust systems – a distinction that matters significantly at scale or during contested elections.`,
  },
  {
    id: 'technology-appetite',
    title: 'Technology appetite is high, but adoption barriers are substantial.',
    content: (data: ExecutiveSummaryData) =>
      `Technology and digitalisation was overwhelmingly the top priority theme, mentioned by ${data.technologyPriorityCount} respondents in open-ended responses. Biometric systems and digital identity solutions have already been explored by the majority of respondents, and interest in innovations like portable credentials and digital achievement recognition was notably strong. However, implementation concerns are equally prominent: resistance to change and skills gaps tied as the most-cited barriers, followed by the need for political and stakeholder buy-in. Several respondents emphasised that technology adoption requires not just infrastructure investment but sustained change management and capacity building.`,
  },
  {
    id: 'path-forward',
    title: 'The path forward requires matching solutions to genuine needs.',
    content: () =>
      `This survey deliberately avoided assuming that any particular technology – blockchain or otherwise – was the answer. The findings confirm that electoral workforce challenges are real and significant, but also highly context-dependent. A solution appropriate for a European jurisdiction with 350 temporary workers and reliable connectivity looks very different from one serving an African election body managing 500,000 workers across areas with intermittent internet access. Over 70% of respondents expressed willingness to participate in follow-up discussions, suggesting strong appetite for collaboration – but any engagement must begin with deep understanding of local constraints and priorities rather than technology-first thinking.`,
  },
];

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { getSummaryStats, getPilotCandidates, getQualitativeSynthesis } from '@/lib/data';

export default function ExecutiveSummary() {
  const stats = getSummaryStats();
  const pilots = getPilotCandidates();
  const qualitative = getQualitativeSynthesis();

  const overview = stats.response_overview;
  const regions = Object.entries(overview.regions);
  const totalResponses = overview.total_responses;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Executive Summary</h1>
        <p className="text-muted-foreground mt-2">
          Electoral Workforce Survey Analysis - ICPS &amp; BSV Association Partnership
        </p>
      </div>

      {/* Qualitative Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Overview</CardTitle>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none space-y-4 text-muted-foreground">
          <p>
            The ICPS Electoral Workforce Survey gathered responses from {totalResponses} electoral
            management bodies across {overview.countries.unique_count} countries, representing a
            diverse cross-section of democratic institutions from Africa ({overview.regions.Africa} responses),
            Asia-Pacific ({overview.regions['Asia-Pacific']} responses), Europe ({overview.regions.Europe} responses),
            and the Americas ({overview.regions.Americas} responses). This problem-discovery initiative,
            conducted in partnership with the BSV Association, prioritised understanding the genuine
            operational realities facing election administrators—the day-to-day challenges of recruiting,
            training, credentialing, and retaining the workforce that makes democratic elections possible.
          </p>
          <p>
            <strong>The workforce challenge is universal but manifests differently across regions.</strong> Election
            management bodies worldwide rely heavily on temporary workers—poll workers, counting staff, and
            election day officials who are recruited, trained, and deployed for specific electoral events.
            The survey reveals that the most pressing challenge is not recruiting these workers initially,
            but retaining institutional knowledge and trained capacity between election cycles. Over 60% of
            respondents cited &quot;losing trained workers to other opportunities between elections&quot; as a
            significant challenge, while many lack any systematic way to track worker performance or
            maintain engagement during non-election periods. This creates a costly cycle of perpetual
            re-recruitment and re-training.
          </p>
          <p>
            <strong>Infrastructure constraints vary dramatically by region.</strong> Budget limitations emerged
            as the dominant barrier, cited by {stats.technology_infrastructure.limitations.option_counts['Budget constraints']} respondents
            ({Math.round((stats.technology_infrastructure.limitations.option_counts['Budget constraints'] as number) / totalResponses * 100)}%),
            but the nature of constraints differs significantly. African jurisdictions face compounding
            challenges: limited internet connectivity affects remote credential verification, insufficient
            IT support hampers system maintenance, and lack of devices prevents digital record-keeping.
            European respondents, by contrast, reported higher confidence in their existing systems but
            identified resistance to change and skills gaps as primary concerns. The Americas showed
            mixed infrastructure maturity, with some jurisdictions managing workforces of 750,000+ temporary
            workers while others operate with fewer than 100.
          </p>
          <p>
            <strong>Credential verification presents operational friction across all contexts.</strong> While
            most respondents reported spending fewer than 5 hours per election on credential verification,
            the challenges are qualitative rather than purely time-based. Difficulty verifying credentials
            in remote or offline locations was the top-cited challenge, followed by time delays and the
            lack of centralised verification systems. These issues compound in jurisdictions with large
            geographic spread or limited connectivity, where a worker&apos;s training history and credentials
            may exist only in paper records at a distant regional office.
          </p>
          <p>
            <strong>Training systems show moderate confidence but fragile foundations.</strong> Respondents
            expressed generally high confidence in their training delivery systems, with 24 of 29 reporting
            they feel &quot;confident&quot; in their training record accuracy. However, when probed about how they
            handle lost or disputed training records, responses revealed heavy reliance on manual fallbacks:
            paper backup records, supervisor judgment calls, or simply excluding workers from deployment.
            This suggests that confidence may be based on low incident rates rather than robust systems—a
            distinction that matters significantly at scale or during contested elections.
          </p>
          <p>
            <strong>Technology appetite is high, but adoption barriers are substantial.</strong> Technology
            and digitalisation was overwhelmingly the top priority theme, mentioned
            by {qualitative.priority_themes.technology_digitalization} respondents in open-ended responses.
            Biometric systems and digital identity solutions have already been explored by the majority of
            respondents, and interest in innovations like portable credentials and digital achievement
            recognition was notably strong. However, implementation concerns are equally prominent:
            resistance to change and skills gaps tied as the most-cited barriers, followed by the need
            for political and stakeholder buy-in. Several respondents emphasised that technology adoption
            requires not just infrastructure investment but sustained change management and capacity building.
          </p>
          <p>
            <strong>The path forward requires matching solutions to genuine needs.</strong> This survey
            deliberately avoided assuming that any particular technology—blockchain or otherwise—was the
            answer. The findings confirm that electoral workforce challenges are real and significant, but
            also highly context-dependent. A solution appropriate for a European jurisdiction with 350
            temporary workers and reliable connectivity looks very different from one serving an African
            election body managing 500,000 workers across areas with intermittent internet access. Over
            70% of respondents expressed willingness to participate in follow-up discussions, suggesting
            strong appetite for collaboration—but any engagement must begin with deep understanding of
            local constraints and priorities rather than technology-first thinking.
          </p>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Responses</CardDescription>
            <CardTitle className="text-4xl">{totalResponses}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              From {overview.countries.unique_count} countries
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>High Potential Pilots</CardDescription>
            <CardTitle className="text-4xl">{pilots.summary.high_potential_count}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Of {pilots.summary.total_assessed} assessed candidates
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Follow-up Interest</CardDescription>
            <CardTitle className="text-4xl">
              {Math.round(((overview.followup_willing?.Yes || 0) + (overview.followup_willing?.['Contact me with more information'] || 0)) / totalResponses * 100)}%
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Willing to participate further
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Top Priority</CardDescription>
            <CardTitle className="text-xl">Technology &amp; Digitalization</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Mentioned by {qualitative.priority_themes.technology_digitalization} respondents
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Regional Distribution */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Regional Distribution</CardTitle>
            <CardDescription>Survey responses by geographic region</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {regions.map(([region, count]) => (
              <div key={region} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{region}</span>
                  <span className="text-sm text-muted-foreground">
                    {count} ({Math.round((count as number) / totalResponses * 100)}%)
                  </span>
                </div>
                <Progress value={(count as number) / totalResponses * 100} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Pilot Candidates</CardTitle>
            <CardDescription>Highest scoring potential implementation partners</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pilots.summary.top_5_candidates.slice(0, 5).map((candidate, idx) => (
                <div key={candidate.country} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-muted-foreground">{idx + 1}</span>
                    <div>
                      <p className="font-medium">{candidate.country}</p>
                      <p className="text-xs text-muted-foreground">{candidate.region}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{candidate.composite_score.toFixed(2)}</span>
                    <Badge variant={candidate.suitability === 'HIGH' ? 'default' : 'secondary'}>
                      {candidate.suitability}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Key Challenges */}
      <Card>
        <CardHeader>
          <CardTitle>Top Infrastructure Challenges</CardTitle>
          <CardDescription>Most frequently cited limitations across all respondents</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(stats.technology_infrastructure.limitations.option_counts)
              .filter(([key]) => !['Open-Ended Response', '0-25%', 'Other'].includes(key))
              .slice(0, 6)
              .map(([challenge, count]) => (
                <div key={challenge} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                  <div className="flex-1">
                    <p className="font-medium text-sm">{challenge}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {count} respondents ({Math.round((count as number) / totalResponses * 100)}%)
                    </p>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Compelling Quote */}
      <Card className="bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle>Voice from the Field</CardTitle>
        </CardHeader>
        <CardContent>
          <blockquote className="text-lg italic">
            &quot;{qualitative.compelling_quotes[0]?.quote}&quot;
          </blockquote>
          <p className="text-sm text-muted-foreground mt-4">
            — Electoral Official, {qualitative.compelling_quotes[0]?.country}
          </p>
        </CardContent>
      </Card>

      {/* Key Findings Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Credential Verification</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Avg verification time</span>
              <span className="font-medium">&lt;5 hours</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Top challenge</span>
              <span className="font-medium text-right text-sm">Remote verification</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Workforce Retention</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Return rate</span>
              <span className="font-medium">51-75%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Top challenge</span>
              <span className="font-medium text-right text-sm">Losing trained workers</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Technology Adoption</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Most explored</span>
              <span className="font-medium text-right text-sm">Biometrics</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Top barrier</span>
              <span className="font-medium text-right text-sm">Budget constraints</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

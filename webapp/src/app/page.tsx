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

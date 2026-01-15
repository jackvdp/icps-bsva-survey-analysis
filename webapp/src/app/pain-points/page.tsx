import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { getPainPointRankings, getSummaryStats } from '@/lib/data';

const areaLabels: Record<string, string> = {
  temporary_workforce: 'Temporary Workforce Management',
  infrastructure: 'Technology Infrastructure',
  data_synchronization: 'Data Synchronization',
  training_systems: 'Training Systems',
  credential_verification: 'Credential Verification',
};

const areaDescriptions: Record<string, string> = {
  temporary_workforce: 'Challenges managing seasonal/temporary election workers',
  infrastructure: 'Limitations in technology, connectivity, and IT support',
  data_synchronization: 'Issues with data consistency across systems and locations',
  training_systems: 'Problems with training record management and verification',
  credential_verification: 'Difficulties verifying worker credentials and identity',
};

export default function PainPointsPage() {
  const rankings = getPainPointRankings();
  const stats = getSummaryStats();
  const maxSeverity = Math.max(...rankings.area_ranking.map((a) => a.avg_severity));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Pain Point Explorer</h1>
        <p className="text-muted-foreground mt-2">
          Operational challenges ranked by severity across all survey respondents
        </p>
      </div>

      {/* Overall Rankings */}
      <Card>
        <CardHeader>
          <CardTitle>Pain Point Areas by Severity</CardTitle>
          <CardDescription>
            Average severity scores across all respondents (higher = more severe)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {rankings.area_ranking.map((area, idx) => (
            <div key={area.area} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-xl font-bold text-muted-foreground w-6">{idx + 1}</span>
                  <div>
                    <p className="font-medium">{areaLabels[area.area] || area.area}</p>
                    <p className="text-sm text-muted-foreground">
                      {areaDescriptions[area.area]}
                    </p>
                  </div>
                </div>
                <span className="text-lg font-semibold">{area.avg_severity.toFixed(2)}</span>
              </div>
              <Progress
                value={(area.avg_severity / maxSeverity) * 100}
                className="h-3"
              />
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Detailed Breakdowns */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Credential Verification Challenges */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Credential Verification Challenges</CardTitle>
            <CardDescription>Top reported issues</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(stats.credential_verification.challenges.option_counts)
              .filter(([key]) => !['Less than 25%', 'Other'].includes(key))
              .slice(0, 5)
              .map(([challenge, count]) => (
                <div key={challenge} className="flex items-center justify-between">
                  <span className="text-sm">{challenge}</span>
                  <span className="text-sm font-medium text-muted-foreground">{count}</span>
                </div>
              ))}
          </CardContent>
        </Card>

        {/* Workforce Management Challenges */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Workforce Management Challenges</CardTitle>
            <CardDescription>Top reported issues</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(stats.temporary_workforce.challenges.option_counts)
              .filter(([key]) => !['Never', 'Rarely (1-5 times per election)', 'Other'].includes(key))
              .slice(0, 5)
              .map(([challenge, count]) => (
                <div key={challenge} className="flex items-center justify-between">
                  <span className="text-sm">{challenge}</span>
                  <span className="text-sm font-medium text-muted-foreground">{count}</span>
                </div>
              ))}
          </CardContent>
        </Card>

        {/* Infrastructure Limitations */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Infrastructure Limitations</CardTitle>
            <CardDescription>Barriers to technology adoption</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(stats.technology_infrastructure.limitations.option_counts)
              .filter(([key]) => !['Open-Ended Response', '0-25%', 'Other'].includes(key))
              .map(([limitation, count]) => (
                <div key={limitation} className="flex items-center justify-between">
                  <span className="text-sm">{limitation}</span>
                  <span className="text-sm font-medium text-muted-foreground">{count}</span>
                </div>
              ))}
          </CardContent>
        </Card>

        {/* Technology Levels */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Technology Infrastructure Levels</CardTitle>
            <CardDescription>Current tech maturity by area</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(stats.technology_infrastructure.levels).map(([area, data]) => (
              <div key={area} className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium capitalize">{area}</span>
                  <span className="text-sm text-muted-foreground">
                    Avg: {data.mean.toFixed(2)} / 3
                  </span>
                </div>
                <div className="flex gap-2 text-xs text-muted-foreground">
                  {Object.entries(data.distribution).map(([level, count]) => (
                    <span key={level}>
                      {level}: {count}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Top Countries by Pain Area */}
      <Card>
        <CardHeader>
          <CardTitle>Highest Pain Point Scores by Country</CardTitle>
          <CardDescription>
            Countries experiencing the most severe challenges in each area
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {rankings.area_ranking.slice(0, 3).map((area) => {
              const areaData = rankings[area.area as keyof typeof rankings];
              if (!areaData || !('scores' in areaData)) return null;
              const topCountries = areaData.scores
                .filter((s: { country: string; score: number }) => s.country && typeof s.country === 'string' && !s.country.includes('NaN'))
                .slice(0, 5);

              return (
                <div key={area.area} className="space-y-3">
                  <h4 className="font-semibold">{areaLabels[area.area]}</h4>
                  <div className="space-y-2">
                    {topCountries.map((country: { country: string; score: number }, idx: number) => (
                      <div key={`${country.country}-${idx}`} className="flex items-center justify-between text-sm">
                        <span>{country.country}</span>
                        <span className="font-medium">{Number(country.score).toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

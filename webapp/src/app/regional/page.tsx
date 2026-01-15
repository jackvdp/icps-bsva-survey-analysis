import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { getRegionalComparison, getRegionColor } from '@/lib/data';

export default function RegionalComparisonPage() {
  const regional = getRegionalComparison();
  const regions = Object.entries(regional);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Regional Comparison</h1>
        <p className="text-muted-foreground mt-2">
          Survey findings broken down by geographic region
        </p>
      </div>

      {/* Region Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {regions.map(([region, data]) => (
          <Card key={region}>
            <CardHeader className="pb-2">
              <CardDescription>{region}</CardDescription>
              <CardTitle className="text-3xl">{data.response_count}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                {data.countries.length} countries represented
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {data.followup_willing_pct.toFixed(0)}% willing for follow-up
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detailed Regional Cards */}
      <div className="grid gap-6 lg:grid-cols-2">
        {regions.map(([region, data]) => (
          <Card key={region}>
            <CardHeader>
              <CardTitle>{region}</CardTitle>
              <CardDescription>
                {data.response_count} responses from {data.countries.length} countries
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Countries */}
              <div>
                <h4 className="text-sm font-medium mb-2">Countries</h4>
                <div className="flex flex-wrap gap-1">
                  {data.countries.map((country) => (
                    <Badge key={country} variant="secondary" className="text-xs">
                      {country}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid gap-4 grid-cols-2">
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Avg Verification Hours</p>
                  <p className="text-lg font-semibold">
                    {data.verification_hours_mean?.toFixed(2) || 'N/A'}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Worker Return Rate</p>
                  <p className="text-lg font-semibold">
                    {data.worker_return_rate_mean?.toFixed(2) || 'N/A'}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Training Confidence</p>
                  <p className="text-lg font-semibold">
                    {data.training_confidence_mean?.toFixed(2) || 'N/A'}/5
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Sync Confidence</p>
                  <p className="text-lg font-semibold">
                    {data.sync_confidence_mean?.toFixed(2) || 'N/A'}/5
                  </p>
                </div>
              </div>

              {/* Technology Levels */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium">Technology Infrastructure</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Recruitment</span>
                    <span className="font-medium">{data.tech_recruitment_mean?.toFixed(2) || 'N/A'}/3</span>
                  </div>
                  <Progress value={(data.tech_recruitment_mean || 0) / 3 * 100} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Training</span>
                    <span className="font-medium">{data.tech_training_mean?.toFixed(2) || 'N/A'}/3</span>
                  </div>
                  <Progress value={(data.tech_training_mean || 0) / 3 * 100} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Performance</span>
                    <span className="font-medium">{data.tech_performance_mean?.toFixed(2) || 'N/A'}/3</span>
                  </div>
                  <Progress value={(data.tech_performance_mean || 0) / 3 * 100} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Communication</span>
                    <span className="font-medium">{data.tech_communication_mean?.toFixed(2) || 'N/A'}/3</span>
                  </div>
                  <Progress value={(data.tech_communication_mean || 0) / 3 * 100} className="h-2" />
                </div>
              </div>

              {/* Top Challenges */}
              <div>
                <h4 className="text-sm font-medium mb-2">Top Infrastructure Limitations</h4>
                <div className="space-y-1">
                  {Object.entries(data.top_infrastructure_limitations)
                    .filter(([key]) => !['0-25%'].includes(key))
                    .slice(0, 4)
                    .map(([limitation, count]) => (
                      <div key={limitation} className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground truncate flex-1">{limitation}</span>
                        <span className="font-medium ml-2">{count}</span>
                      </div>
                    ))}
                </div>
              </div>

              {/* Top Credential Challenges */}
              <div>
                <h4 className="text-sm font-medium mb-2">Top Credential Challenges</h4>
                <div className="space-y-1">
                  {Object.entries(data.top_credential_challenges)
                    .slice(0, 4)
                    .map(([challenge, count]) => (
                      <div key={challenge} className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground truncate flex-1">{challenge}</span>
                        <span className="font-medium ml-2">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Cross-Regional Comparison Table */}
      <Card>
        <CardHeader>
          <CardTitle>Cross-Regional Metrics Comparison</CardTitle>
          <CardDescription>Key indicators side-by-side</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 font-medium">Metric</th>
                  {regions.map(([region]) => (
                    <th key={region} className="text-right py-2 font-medium">{region}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-2">Response Count</td>
                  {regions.map(([region, data]) => (
                    <td key={region} className="text-right py-2">{data.response_count}</td>
                  ))}
                </tr>
                <tr className="border-b">
                  <td className="py-2">Follow-up Willing %</td>
                  {regions.map(([region, data]) => (
                    <td key={region} className="text-right py-2">{data.followup_willing_pct.toFixed(0)}%</td>
                  ))}
                </tr>
                <tr className="border-b">
                  <td className="py-2">Avg Completion Score</td>
                  {regions.map(([region, data]) => (
                    <td key={region} className="text-right py-2">{data.avg_completion_score.toFixed(1)}</td>
                  ))}
                </tr>
                <tr className="border-b">
                  <td className="py-2">Verification Hours (mean)</td>
                  {regions.map(([region, data]) => (
                    <td key={region} className="text-right py-2">{data.verification_hours_mean?.toFixed(2) || 'N/A'}</td>
                  ))}
                </tr>
                <tr className="border-b">
                  <td className="py-2">Training Confidence</td>
                  {regions.map(([region, data]) => (
                    <td key={region} className="text-right py-2">{data.training_confidence_mean?.toFixed(2) || 'N/A'}</td>
                  ))}
                </tr>
                <tr className="border-b">
                  <td className="py-2">Tech - Recruitment</td>
                  {regions.map(([region, data]) => (
                    <td key={region} className="text-right py-2">{data.tech_recruitment_mean?.toFixed(2) || 'N/A'}</td>
                  ))}
                </tr>
                <tr>
                  <td className="py-2">Tech - Training</td>
                  {regions.map(([region, data]) => (
                    <td key={region} className="text-right py-2">{data.tech_training_mean?.toFixed(2) || 'N/A'}</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

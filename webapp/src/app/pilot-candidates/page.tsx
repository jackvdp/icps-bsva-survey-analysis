import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { getPilotCandidates } from '@/lib/data';

function getSuitabilityVariant(suitability: string): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (suitability === 'HIGH') return 'default';
  if (suitability === 'MEDIUM') return 'secondary';
  return 'outline';
}

export default function PilotCandidatesPage() {
  const pilots = getPilotCandidates();
  const { all_candidates, high_potential, medium_potential, summary, scoring_methodology } = pilots;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Pilot Candidates</h1>
        <p className="text-muted-foreground mt-2">
          Electoral Management Bodies assessed for blockchain pilot implementation potential
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Assessed</CardDescription>
            <CardTitle className="text-4xl">{summary.total_assessed}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="border-green-500/50 bg-green-500/5">
          <CardHeader className="pb-2">
            <CardDescription>High Potential</CardDescription>
            <CardTitle className="text-4xl text-green-600">{summary.high_potential_count}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="border-yellow-500/50 bg-yellow-500/5">
          <CardHeader className="pb-2">
            <CardDescription>Medium Potential</CardDescription>
            <CardTitle className="text-4xl text-yellow-600">{summary.medium_potential_count}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Low Potential</CardDescription>
            <CardTitle className="text-4xl text-muted-foreground">{summary.low_potential_count}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* High Potential Candidates */}
      {high_potential.length > 0 && (
        <Card className="border-green-500/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full bg-green-500" />
              High Potential Candidates
            </CardTitle>
            <CardDescription>
              Strong combination of need, capability, and willingness for pilot implementation
            </CardDescription>
          </CardHeader>
          <CardContent>
            {high_potential.map((candidate) => (
              <div key={candidate.country} className="border rounded-lg p-4 space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-xl font-semibold">{candidate.country}</h3>
                    <p className="text-sm text-muted-foreground">{candidate.region}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold">{candidate.composite_score.toFixed(2)}</p>
                    <Badge variant="default">HIGH</Badge>
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Need Score</span>
                      <span className="font-medium">{candidate.need_score}/10</span>
                    </div>
                    <Progress value={candidate.need_score * 10} className="h-2" />
                    <p className="text-xs text-muted-foreground">
                      {candidate.need_components.join(', ') || 'No specific components'}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Capability Score</span>
                      <span className="font-medium">{candidate.capability_score}/10</span>
                    </div>
                    <Progress value={candidate.capability_score * 10} className="h-2" />
                    <p className="text-xs text-muted-foreground">
                      {candidate.capability_components.join(', ') || 'No specific components'}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Willingness Score</span>
                      <span className="font-medium">{candidate.willingness_score}/5</span>
                    </div>
                    <Progress value={candidate.willingness_score * 20} className="h-2" />
                    <p className="text-xs text-muted-foreground">
                      {candidate.willingness_components.join(', ') || 'No specific components'}
                    </p>
                  </div>
                </div>
                {candidate.scale && (
                  <div className="text-sm text-muted-foreground border-t pt-3">
                    <span className="font-medium">Scale: </span>
                    {candidate.scale.temp_workers_count && `~${candidate.scale.temp_workers_count} temp workers`}
                    {candidate.scale.elections_annually && ` • ${candidate.scale.elections_annually}`}
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Medium Potential Candidates */}
      {medium_potential.length > 0 && (
        <Card className="border-yellow-500/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full bg-yellow-500" />
              Medium Potential Candidates
            </CardTitle>
            <CardDescription>
              Moderate fit for pilot implementation - may need additional support
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {medium_potential.map((candidate) => (
              <div key={candidate.country} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-semibold">{candidate.country}</h3>
                    <p className="text-sm text-muted-foreground">{candidate.region}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold">{candidate.composite_score.toFixed(2)}</p>
                    <Badge variant="secondary">MEDIUM</Badge>
                  </div>
                </div>
                <div className="grid gap-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Need</span>
                    <span>{candidate.need_score}/10</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Capability</span>
                    <span>{candidate.capability_score}/10</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Willingness</span>
                    <span>{candidate.willingness_score}/5</span>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* All Candidates Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Assessed Candidates</CardTitle>
          <CardDescription>
            Complete list sorted by composite score
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Country</TableHead>
                <TableHead>Region</TableHead>
                <TableHead className="text-right">Need</TableHead>
                <TableHead className="text-right">Capability</TableHead>
                <TableHead className="text-right">Willingness</TableHead>
                <TableHead className="text-right">Composite</TableHead>
                <TableHead>Suitability</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {all_candidates.map((candidate, idx) => (
                <TableRow key={`${candidate.country}-${idx}`}>
                  <TableCell className="font-medium">{candidate.country}</TableCell>
                  <TableCell>{candidate.region}</TableCell>
                  <TableCell className="text-right">{candidate.need_score.toFixed(1)}</TableCell>
                  <TableCell className="text-right">{candidate.capability_score.toFixed(1)}</TableCell>
                  <TableCell className="text-right">{candidate.willingness_score}</TableCell>
                  <TableCell className="text-right font-semibold">
                    {candidate.composite_score.toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getSuitabilityVariant(candidate.suitability)}>
                      {candidate.suitability}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Scoring Methodology */}
      <Card>
        <CardHeader>
          <CardTitle>Scoring Methodology</CardTitle>
          <CardDescription>
            How pilot candidates are assessed and ranked
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <h4 className="font-semibold">Need Score (0-10)</h4>
              <p className="text-sm text-muted-foreground">{String(scoring_methodology.need_score)}</p>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold">Capability Score (0-10)</h4>
              <p className="text-sm text-muted-foreground">{String(scoring_methodology.capability_score)}</p>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold">Willingness Score (0-5)</h4>
              <p className="text-sm text-muted-foreground">{String(scoring_methodology.willingness_score)}</p>
            </div>
          </div>
          <div className="border-t pt-4">
            <h4 className="font-semibold mb-2">Composite Formula</h4>
            <code className="text-sm bg-muted px-2 py-1 rounded">
              {String(scoring_methodology.composite_formula)}
            </code>
          </div>
          <div className="border-t pt-4">
            <h4 className="font-semibold mb-2">Suitability Criteria</h4>
            <div className="grid gap-2 text-sm">
              {Object.entries(scoring_methodology.suitability_criteria as Record<string, string>).map(([level, criteria]) => (
                <div key={level} className="flex gap-2">
                  <Badge variant={getSuitabilityVariant(level)}>{level}</Badge>
                  <span className="text-muted-foreground">{criteria}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

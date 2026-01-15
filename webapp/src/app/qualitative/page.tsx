import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { getQualitativeSynthesis } from '@/lib/data';

const themeLabels: Record<string, string> = {
  technology_digitalization: 'Technology & Digitalization',
  training_capacity: 'Training & Capacity Building',
  voter_registration: 'Voter Registration',
  funding_resources: 'Funding & Resources',
  transparency_trust: 'Transparency & Trust',
  security_integrity: 'Security & Integrity',
  accessibility_inclusion: 'Accessibility & Inclusion',
  staff_recruitment: 'Staff Recruitment',
  other: 'Other',
};

const concernLabels: Record<string, string> = {
  'Resistance to change': 'Resistance to Change',
  'Trust/confidence issues': 'Trust & Confidence Issues',
  'Security concerns': 'Security Concerns',
  'Infrastructure gaps': 'Infrastructure Gaps',
  'Political/stakeholder buy-in': 'Political/Stakeholder Buy-in',
  'Skills/training gaps': 'Skills & Training Gaps',
  'Funding/cost concerns': 'Funding & Cost Concerns',
};

const categoryColors: Record<string, string> = {
  'Implementation Concern': 'bg-yellow-500',
  'Tech Adoption Barrier': 'bg-red-500',
  'Vision for Change': 'bg-green-500',
};

export default function QualitativeInsightsPage() {
  const synthesis = getQualitativeSynthesis();
  const maxPriorityCount = Math.max(...Object.values(synthesis.priority_themes));
  const maxConcernCount = Math.max(...Object.values(synthesis.concern_themes));
  const maxChangeCount = Math.max(...Object.values(synthesis.change_themes));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Qualitative Insights</h1>
        <p className="text-muted-foreground mt-2">
          Themes and quotes extracted from open-ended survey responses
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          Based on {synthesis.total_responses_analyzed} responses analyzed
        </p>
      </div>

      {/* Priority Themes */}
      <Card>
        <CardHeader>
          <CardTitle>Priority Themes</CardTitle>
          <CardDescription>
            What respondents identified as their top operational priorities
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(synthesis.priority_themes)
            .sort(([, a], [, b]) => b - a)
            .map(([theme, count]) => (
              <div key={theme} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{themeLabels[theme] || theme}</span>
                  <span className="text-sm text-muted-foreground">{count} mentions</span>
                </div>
                <Progress value={(count / maxPriorityCount) * 100} className="h-2" />
              </div>
            ))}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Implementation Concerns */}
        <Card>
          <CardHeader>
            <CardTitle>Implementation Concerns</CardTitle>
            <CardDescription>
              Barriers and worries about adopting new systems
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(synthesis.concern_themes)
              .sort(([, a], [, b]) => b - a)
              .map(([concern, count]) => (
                <div key={concern} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{concernLabels[concern] || concern}</span>
                    <span className="text-sm text-muted-foreground">{count}</span>
                  </div>
                  <Progress value={(count / maxConcernCount) * 100} className="h-2" />
                </div>
              ))}
          </CardContent>
        </Card>

        {/* Desired Changes */}
        <Card>
          <CardHeader>
            <CardTitle>Desired Changes</CardTitle>
            <CardDescription>
              What respondents want to see improved
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(synthesis.change_themes)
              .sort(([, a], [, b]) => b - a)
              .map(([theme, count]) => (
                <div key={theme} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{theme}</span>
                    <span className="text-sm text-muted-foreground">{count}</span>
                  </div>
                  <Progress value={(count / maxChangeCount) * 100} className="h-2" />
                </div>
              ))}
          </CardContent>
        </Card>
      </div>

      {/* Compelling Quotes */}
      <Card>
        <CardHeader>
          <CardTitle>Voices from the Field</CardTitle>
          <CardDescription>
            Selected quotes that illustrate key themes and challenges
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {synthesis.compelling_quotes.map((quote, idx) => (
            <div
              key={idx}
              className="border-l-4 pl-4 py-2"
              style={{
                borderColor: quote.category === 'Vision for Change'
                  ? 'rgb(34, 197, 94)'
                  : quote.category === 'Tech Adoption Barrier'
                  ? 'rgb(239, 68, 68)'
                  : 'rgb(234, 179, 8)',
              }}
            >
              <blockquote className="text-base italic text-foreground">
                &ldquo;{quote.quote}&rdquo;
              </blockquote>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-sm font-medium">{quote.country}</span>
                <Badge
                  variant="outline"
                  className={`text-xs ${
                    quote.category === 'Vision for Change'
                      ? 'border-green-500 text-green-600'
                      : quote.category === 'Tech Adoption Barrier'
                      ? 'border-red-500 text-red-600'
                      : 'border-yellow-500 text-yellow-600'
                  }`}
                >
                  {quote.category}
                </Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Key Takeaways */}
      <Card className="bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle>Key Takeaways</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <h4 className="font-semibold text-green-600">Opportunities</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Strong interest in technology and digitalization</li>
                <li>• Desire for improved transparency in results</li>
                <li>• Openness to new training approaches</li>
                <li>• Recognition of need for better workforce management</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold text-red-600">Challenges</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Resistance to change from staff and stakeholders</li>
                <li>• Skills gaps and training needs</li>
                <li>• Budget and infrastructure constraints</li>
                <li>• Need for political buy-in and trust building</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

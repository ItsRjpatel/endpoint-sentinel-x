import { AlertTriangle, TrendingUp } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../../components/ui/Card';
import { EndpointDetails, RiskLevel } from '../../types';

interface RiskScoreCardProps {
  endpoint: EndpointDetails;
}

const RISK_META: Record<RiskLevel, { label: string; ring: string; text: string; bg: string }> = {
  low: { label: 'Low', ring: '#10b981', text: 'text-success', bg: 'bg-success/10' },
  medium: { label: 'Medium', ring: '#f59e0b', text: 'text-warning', bg: 'bg-warning/10' },
  high: { label: 'High', ring: '#f97316', text: 'text-warning', bg: 'bg-warning/10' },
  critical: { label: 'Critical', ring: '#ef4444', text: 'text-danger', bg: 'bg-danger/10' },
};

const weightDot: Record<'high' | 'medium' | 'low', string> = {
  high: 'bg-danger',
  medium: 'bg-warning',
  low: 'bg-text-muted',
};

export function RiskScoreCard({ endpoint }: RiskScoreCardProps) {
  const level = endpoint.riskLevel ?? 'medium';
  const meta = RISK_META[level];
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const score = endpoint.riskScore ?? 50;
  const pct = Math.min(Math.max(score, 0), 100) / 100;
  const offset = circumference * (1 - pct);
  const factors = endpoint.riskFactors ?? [];

  return (
    <Card className="h-full">
      <CardHeader className="pb-3 border-b border-border flex-row items-center justify-between space-y-0">
        <CardTitle className="text-base">Risk Score</CardTitle>
        <span className="flex items-center gap-1 text-xs font-medium text-text-muted">
          <TrendingUp className="h-3.5 w-3.5 text-danger" aria-hidden="true" />
          +6 this week
        </span>
      </CardHeader>
      <CardContent className="pt-5">
        <div className="flex items-center gap-5">
          <div className="relative h-28 w-28 shrink-0">
            <svg viewBox="0 0 100 100" className="h-28 w-28 -rotate-90">
              <circle cx="50" cy="50" r={radius} fill="none" stroke="currentColor" strokeWidth="8" className="text-surface-secondary" />
              <circle
                cx="50"
                cy="50"
                r={radius}
                fill="none"
                stroke={meta.ring}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold tabular-nums text-text-primary">{score}</span>
              <span className="text-[10px] text-text-muted">/ 100</span>
            </div>
          </div>

          <div className="min-w-0 flex-1">
            <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${meta.bg} ${meta.text}`}>
              <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
              {meta.label} risk
            </span>
            <p className="mt-2 text-xs leading-5 text-text-muted">
              Score reflects unresolved vulnerabilities, active alerts, and control drift.
            </p>
          </div>
        </div>

        <ul className="mt-5 space-y-2 border-t border-border pt-4">
          {factors.map((f) => (
            <li key={f.label} className="flex items-start gap-2.5 text-xs text-text-secondary">
              <span className={`mt-1 h-1.5 w-1.5 shrink-0 rounded-full ${weightDot[f.weight]}`} aria-hidden="true" />
              <span className="leading-5">{f.label}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

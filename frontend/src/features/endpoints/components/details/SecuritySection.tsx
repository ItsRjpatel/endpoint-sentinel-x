import { CheckCircle2, XCircle, ShieldCheck, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../../components/ui/Card';
import { Badge } from '../../../../components/ui/Badge';
import { EndpointDetails } from '../../types';
import { useEndpointSecurity } from '../../../security/hooks/useSecurity';
import { Skeleton } from '../../../../components/ui/Skeleton';

interface SecuritySectionProps {
  endpoint: EndpointDetails;
}

function getScoreVariant(score: number): 'success' | 'warning' | 'danger' {
  if (score >= 80) return 'success';
  if (score >= 60) return 'warning';
  return 'danger';
}

function ControlRow({ label, enabled, note }: { label: string; enabled: boolean; note?: string }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border last:border-0">
      <span className="text-sm text-text-secondary">{label}</span>
      {enabled ? (
        <span className="flex items-center gap-1.5 text-xs font-medium text-success">
          <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
          {note ?? 'On'}
        </span>
      ) : (
        <span className="flex items-center gap-1.5 text-xs font-medium text-danger">
          <XCircle className="h-4 w-4" aria-hidden="true" />
          {note ?? 'Off'}
        </span>
      )}
    </div>
  );
}

export function SecuritySection({ endpoint }: SecuritySectionProps) {
  const { data: securitySummary, isLoading } = useEndpointSecurity(Number(endpoint.id));
  
  // Fallback to basic inventory properties if security summary is loading/failed
  const s = endpoint.security;

  if (isLoading) {
    return (
      <Card className="h-full">
        <CardHeader className="pb-3 border-b border-border flex-row items-center justify-between space-y-0">
          <CardTitle className="text-base flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-text-muted" aria-hidden="true" />
            Security Posture
          </CardTitle>
          <Skeleton className="h-5 w-16 rounded-full" />
        </CardHeader>
        <CardContent className="pt-4 space-y-3">
          {[1, 2, 3, 4, 5, 6].map(i => <Skeleton key={i} className="h-6 w-full" />)}
        </CardContent>
      </Card>
    );
  }

  const score = securitySummary?.score?.total_score ?? endpoint.securityScore;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3 border-b border-border flex-row items-center justify-between space-y-0 shrink-0">
        <CardTitle className="text-base flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-text-muted" aria-hidden="true" />
          Security Posture
        </CardTitle>
        <Badge variant={getScoreVariant(score)}>{Math.round(score)} / 100</Badge>
      </CardHeader>
      <CardContent className="pt-2 flex-1 overflow-y-auto">
        <ControlRow label="Firewall" enabled={s.firewallEnabled} />
        <ControlRow label="Microsoft Defender" enabled={s.defenderActive} />
        <ControlRow label="Real-time protection" enabled={s.realTimeProtection} />
        <ControlRow label="BitLocker encryption" enabled={s.bitlockerEnabled} />
        <ControlRow label="Secure Boot" enabled={s.secureBootEnabled} />
        <ControlRow
          label="TPM"
          enabled={s.tpmPresent}
          note={s.tpmPresent ? `Version ${s.tpmVersion}` : 'Not present'}
        />

        {securitySummary?.recommendations && securitySummary.recommendations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border">
            <h4 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-warning" />
              Recommendations
            </h4>
            <div className="space-y-3">
              {securitySummary.recommendations.map(rec => (
                <div key={rec.id} className="bg-surface-secondary/50 p-3 rounded-lg border border-border">
                  <p className="text-xs font-medium text-text-primary">{rec.title}</p>
                  <p className="text-xs text-text-muted mt-1">{rec.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

import React from 'react';
import { Fingerprint, Tag, Network as NetworkIcon } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../../components/ui/Card';
import { EndpointDetails } from '../../types';

interface DeviceSummaryProps {
  endpoint: EndpointDetails;
}

function Row({ label, value }: { label: string; value: string | React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 py-2.5 border-b border-border last:border-0">
      <span className="text-xs text-text-muted">{label}</span>
      <span className="min-w-0 truncate text-sm font-medium text-text-primary text-right">{value || '—'}</span>
    </div>
  );
}

export function DeviceSummary({ endpoint }: DeviceSummaryProps) {
  return (
    <Card className="h-full">
      <CardHeader className="pb-3 border-b border-border">
        <CardTitle className="text-base flex items-center gap-2">
          <Fingerprint className="h-4 w-4 text-text-muted" aria-hidden="true" />
          Device Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-text-muted">
          <Tag className="h-3 w-3" aria-hidden="true" /> Identity
        </div>
        <Row label="Manufacturer" value={endpoint.manufacturer} />
        <Row label="Model" value={endpoint.model} />
        <Row label="Serial number" value={<span className="font-mono">{endpoint.serialNumber}</span>} />
        <Row label="Asset tag" value={endpoint.assetTag} />
        <Row label="Operating system" value={endpoint.operatingSystem.name} />
        <Row label="OS version" value={`${endpoint.operatingSystem.version} (${endpoint.operatingSystem.build})`} />

        <div className="mb-1 mt-4 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-text-muted">
          <NetworkIcon className="h-3 w-3" aria-hidden="true" /> Network
        </div>
        <Row label="Domain" value={endpoint.domain} />
        <Row label="Logged-in user" value={endpoint.user} />
        <Row label="IP address" value={<span className="font-mono">{endpoint.ipAddress}</span>} />
        <Row label="MAC address" value={<span className="font-mono">{endpoint.macAddress}</span>} />
      </CardContent>
    </Card>
  );
}

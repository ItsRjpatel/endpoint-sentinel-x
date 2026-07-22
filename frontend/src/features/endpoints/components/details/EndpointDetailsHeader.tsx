import { ArrowLeft, Monitor, Laptop, Server, User, Wifi, Globe, Clock, ShieldOff } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Badge } from '../../../../components/ui/Badge';
import { EndpointDetails } from '../../types/endpoint';
import { EndpointQuickActions } from './EndpointQuickActions';

interface EndpointDetailsHeaderProps {
  endpoint: EndpointDetails;
}

const STATUS_DOT: Record<string, string> = {
  online: 'bg-success',
  offline: 'bg-danger',
  inactive: 'bg-warning',
};

const DEVICE_ICON = { server: Server, desktop: Monitor, laptop: Laptop } as const;

export function EndpointDetailsHeader({ endpoint }: EndpointDetailsHeaderProps) {
  const DeviceIcon = DEVICE_ICON[endpoint.deviceType];

  return (
    <div className="flex flex-col gap-5">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="text-sm">
        <ol className="flex items-center gap-2 text-text-muted">
          <li>
            <Link to="/endpoints" className="hover:text-text-primary transition-colors">
              Endpoints
            </Link>
          </li>
          <li aria-hidden="true">/</li>
          <li>
            <span className="font-medium text-text-primary" aria-current="page">
              {endpoint.hostname}
            </span>
          </li>
        </ol>
      </nav>

      {endpoint.isolated && (
        <div className="flex items-center gap-2 rounded-md border border-danger/30 bg-danger/10 px-4 py-2.5 text-sm text-danger">
          <ShieldOff className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span className="font-medium">This device is network-isolated.</span>
          <span className="text-danger/80">Only Defender-related traffic is permitted.</span>
        </div>
      )}

      <div className="flex flex-col gap-5 rounded-xl border border-border bg-card p-5 sm:p-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex items-start gap-4 min-w-0">
          <Link
            to="/endpoints"
            className="mt-1 shrink-0 rounded-full p-2 text-text-muted hover:bg-surface-secondary hover:text-text-primary transition-colors"
            aria-label="Back to inventory"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>

          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-border bg-surface-secondary text-primary">
            <DeviceIcon className="h-5 w-5" />
          </span>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="text-xl font-bold tracking-tight text-text-primary truncate">{endpoint.hostname}</h1>
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-text-secondary">
                <span className={`h-2 w-2 rounded-full ${STATUS_DOT[endpoint.status]}`} aria-hidden="true" />
                <span className="capitalize">{endpoint.status}</span>
              </span>
              <Badge variant="info">Intune managed</Badge>
              {endpoint.openAlertsCount && endpoint.openAlertsCount > 0 ? (
                <Badge variant="danger">{endpoint.openAlertsCount} open alerts</Badge>
              ) : null}
            </div>

            <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-text-muted">
              <span className="flex items-center gap-1.5">
                <User className="h-3.5 w-3.5" aria-hidden="true" />
                {endpoint.user}
              </span>
              <span className="flex items-center gap-1.5">
                <Wifi className="h-3.5 w-3.5" aria-hidden="true" />
                <span className="font-mono">{endpoint.ipAddress}</span>
              </span>
              <span className="flex items-center gap-1.5">
                <Globe className="h-3.5 w-3.5" aria-hidden="true" />
                {endpoint.domain}
              </span>
              <span className="flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5" aria-hidden="true" />
                Last seen{' '}
                {new Intl.DateTimeFormat(undefined, {
                  month: 'short',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: 'numeric',
                }).format(new Date(endpoint.lastSeen))}
              </span>
            </div>
          </div>
        </div>

        <div className="shrink-0 lg:pl-4">
          <EndpointQuickActions endpoint={endpoint} />
        </div>
      </div>
    </div>
  );
}

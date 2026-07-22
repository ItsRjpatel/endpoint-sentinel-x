import { Activity, Download, ShieldAlert, LogIn, Power, Terminal, ShieldCheck, PowerOff, ShieldOff } from 'lucide-react';
import { Badge } from '../../../../components/ui/Badge';
import { EndpointDetails, TimelineEvent } from '../../types';

interface ActivityTimelineProps {
  endpoint: EndpointDetails;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const EVENT_ICON: Record<TimelineEvent['type'], any> = {
  'User Login': LogIn,
  'Windows Update': Download,
  'Software Installed': Download,
  'Alert Created': ShieldAlert,
  'Policy Applied': ShieldCheck,
  Restart: Power,
  Shutdown: PowerOff,
  'Command Executed': Terminal,
  Isolation: ShieldOff,
  'Agent Connected': Activity,
  'Agent Disconnected': PowerOff,
};

const EVENT_COLOR: Record<TimelineEvent['type'], string> = {
  'User Login': 'text-primary',
  'Windows Update': 'text-success',
  'Software Installed': 'text-primary',
  'Alert Created': 'text-danger',
  'Policy Applied': 'text-success',
  Restart: 'text-warning',
  Shutdown: 'text-danger',
  'Command Executed': 'text-primary',
  Isolation: 'text-danger',
  'Agent Connected': 'text-success',
  'Agent Disconnected': 'text-warning',
};

const severityVariant = { success: 'success', warning: 'warning', error: 'danger', info: 'info', default: 'default' } as const;

export function ActivityTimeline({ endpoint }: ActivityTimelineProps) {
  const timeline = endpoint.timeline;

  return (
    <div className="space-y-5">
      <h3 className="text-sm font-semibold text-text-primary">Activity timeline</h3>

      {timeline.length === 0 ? (
        <div className="rounded-lg border border-border bg-surface-secondary/40 py-10 text-center text-sm text-text-muted">
          No activity recorded.
        </div>
      ) : (
        <ol className="relative ml-3 space-y-6 border-l border-border pl-6">
          {timeline.map((event) => {
            const Icon = EVENT_ICON[event.type] ?? Activity;
            return (
              <li key={event.id} className="relative">
                <span className="absolute -left-[31px] top-0.5 flex h-6 w-6 items-center justify-center rounded-full border-2 border-border bg-card">
                  <Icon className={`h-3.5 w-3.5 ${EVENT_COLOR[event.type]}`} aria-hidden="true" />
                </span>

                <div className="rounded-lg border border-border bg-card p-3.5">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-text-primary">{event.type}</span>
                      <Badge variant={severityVariant[event.severity]}>{event.severity}</Badge>
                    </div>
                    <time className="text-xs font-medium text-text-muted whitespace-nowrap">
                      {new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(event.timestamp))}
                    </time>
                  </div>
                  <p className="mt-1.5 text-sm text-text-secondary">{event.message}</p>
                </div>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}

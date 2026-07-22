import { Badge } from '../../../../components/ui/Badge';
import { EndpointDetails } from '../../types';

interface UpdatesTabProps {
  endpoint: EndpointDetails;
}

const statusVariant = { Installed: 'success', Pending: 'warning', Failed: 'danger' } as const;

export function UpdatesTab({ endpoint }: UpdatesTabProps) {
  const updates = endpoint.updates;
  const pendingCount = updates.filter((u) => u.status === 'Pending').length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Windows updates</h3>
        {pendingCount > 0 && <Badge variant="warning">{pendingCount} pending</Badge>}
      </div>

      <div className="overflow-hidden rounded-lg border border-border">
        <table className="min-w-full divide-y divide-border">
          <thead className="bg-surface-secondary/70">
            <tr>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">KB number</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Title</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Installed</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border bg-card">
            {updates.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-10 text-center text-sm text-text-muted">No updates found.</td>
              </tr>
            ) : (
              updates.map((u) => (
                <tr key={u.kbNumber} className="hover:bg-surface-secondary/50 transition-colors">
                  <td className="px-4 py-2.5 text-sm font-medium text-text-primary">{u.kbNumber}</td>
                  <td className="px-4 py-2.5 text-sm text-text-secondary max-w-sm truncate">{u.title}</td>
                  <td className="px-4 py-2.5 text-sm text-text-muted">
                    {u.installedDate
                      ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(u.installedDate))
                      : '—'}
                  </td>
                  <td className="px-4 py-2.5">
                    <Badge variant={statusVariant[u.status]}>{u.status}</Badge>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import { User, ShieldAlert } from 'lucide-react';
import { Badge } from '../../../../components/ui/Badge';
import { EndpointDetails } from '../../types';

interface UsersTabProps {
  endpoint: EndpointDetails;
}

export function UsersTab({ endpoint }: UsersTabProps) {
  const users = endpoint.users;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Local users</h3>
        <span className="text-xs text-text-muted">{users.length} accounts</span>
      </div>

      <div className="overflow-hidden rounded-lg border border-border">
        <table className="min-w-full divide-y divide-border">
          <thead className="bg-surface-secondary/70">
            <tr>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Username</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Status</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Privileges</th>
              <th className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase tracking-wide text-text-muted">Last login</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border bg-card">
            {users.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-10 text-center text-sm text-text-muted">No users found.</td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.username} className="hover:bg-surface-secondary/50 transition-colors">
                  <td className="px-4 py-2.5 text-sm font-medium text-text-primary">
                    <span className="flex items-center gap-2">
                      <User className="h-3.5 w-3.5 text-text-muted" aria-hidden="true" />
                      {user.username}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <Badge variant={user.enabled ? 'success' : 'default'}>{user.enabled ? 'Enabled' : 'Disabled'}</Badge>
                  </td>
                  <td className="px-4 py-2.5">
                    {user.administrator ? (
                      <span className="flex items-center gap-1.5 text-sm font-medium text-danger">
                        <ShieldAlert className="h-3.5 w-3.5" aria-hidden="true" />
                        Administrator
                      </span>
                    ) : (
                      <span className="text-sm text-text-secondary">Standard user</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-sm text-text-muted">
                    {user.lastLogin
                      ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(user.lastLogin))
                      : 'Never'}
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

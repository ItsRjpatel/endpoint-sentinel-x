import { useState, useMemo } from 'react';
import { usePolicies } from '../hooks/usePolicies';
import { WidgetErrorBoundary } from '../../../components/layout/WidgetErrorBoundary';
import { Badge } from '../../../components/ui/Badge';
import { Card } from '../../../components/ui/Card';
import { Shield, ShieldAlert, CheckCircle2, XCircle, Search, SlidersHorizontal, Plus } from 'lucide-react';

export function PoliciesList() {
  const { data: policies = [], isLoading, error } = usePolicies();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');

  const filteredPolicies = useMemo(() => {
    return policies.filter((policy) => {
      const matchesSearch = policy.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                            (policy.description && policy.description.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesCategory = filterCategory === 'all' || policy.category === filterCategory;
      return matchesSearch && matchesCategory;
    });
  }, [policies, searchTerm, filterCategory]);

  const categories = useMemo(() => {
    const cats = new Set(policies.map(p => p.category));
    return ['all', ...Array.from(cats)];
  }, [policies]);

  if (error) {
    return (
      <div className="p-6">
        <Card className="p-6 bg-danger/10 border-danger/20 text-danger flex items-center gap-3">
          <ShieldAlert className="h-6 w-6" />
          <div>
            <h3 className="font-semibold">Failed to load policies</h3>
            <p className="text-sm opacity-90">There was an error communicating with the policy engine.</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-6 min-h-screen bg-surface-primary">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-text-primary">Enterprise Policies</h1>
          <p className="text-text-muted mt-1 text-sm">Manage security, compliance, and operational configurations.</p>
        </div>
        <button className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors">
          <Plus className="h-4 w-4" />
          New Policy
        </button>
      </div>

      <WidgetErrorBoundary title="Policy Engine">
        <div className="flex flex-col gap-4">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between p-4 rounded-xl border border-border bg-card shadow-sm">
            <div className="relative w-full sm:max-w-xs">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
              <input
                type="text"
                placeholder="Search policies..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-lg border border-border bg-surface-secondary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <SlidersHorizontal className="h-4 w-4 text-text-muted" />
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="w-full sm:w-auto pl-3 pr-8 py-2 rounded-lg border border-border bg-surface-secondary text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 appearance-none"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>
                    {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden flex flex-col">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-surface-secondary border-b border-border">
                  <tr>
                    <th className="px-6 py-4 font-semibold text-text-primary">Policy Name</th>
                    <th className="px-6 py-4 font-semibold text-text-primary">Status</th>
                    <th className="px-6 py-4 font-semibold text-text-primary">Category</th>
                    <th className="px-6 py-4 font-semibold text-text-primary">Priority</th>
                    <th className="px-6 py-4 font-semibold text-text-primary">Version</th>
                    <th className="px-6 py-4 font-semibold text-text-primary text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {isLoading ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-text-muted">
                        <div className="flex items-center justify-center gap-2">
                          <Shield className="h-5 w-5 animate-pulse text-primary" />
                          <span>Loading policy definitions...</span>
                        </div>
                      </td>
                    </tr>
                  ) : filteredPolicies.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-text-muted">
                        <div className="flex flex-col items-center justify-center gap-2">
                          <Shield className="h-8 w-8 text-border" />
                          <span>No policies found matching criteria.</span>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    filteredPolicies.map((policy) => (
                      <tr key={policy.id} className="hover:bg-surface-secondary/50 transition-colors group">
                        <td className="px-6 py-4">
                          <div className="flex flex-col">
                            <span className="font-medium text-text-primary">{policy.name}</span>
                            {policy.description && (
                              <span className="text-xs text-text-muted truncate max-w-[300px]">
                                {policy.description}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {policy.enabled ? (
                            <Badge variant="success" className="gap-1.5 pl-1.5">
                              <CheckCircle2 className="h-3.5 w-3.5" />
                              Active
                            </Badge>
                          ) : (
                            <Badge variant="default" className="gap-1.5 pl-1.5">
                              <XCircle className="h-3.5 w-3.5 opacity-70" />
                              Disabled
                            </Badge>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <Badge variant="info" className="capitalize">
                            {policy.category}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 text-text-secondary">
                          {policy.priority}
                        </td>
                        <td className="px-6 py-4 text-text-secondary font-mono text-xs">
                          v{policy.current_version}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button className="text-primary hover:text-primary/80 font-medium text-sm transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100">
                            Configure
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            
            {/* Simple Pagination Footer for visual completion */}
            <div className="px-6 py-4 border-t border-border bg-surface-secondary/30 flex items-center justify-between text-sm text-text-muted">
              <span>Showing {filteredPolicies.length} {filteredPolicies.length === 1 ? 'policy' : 'policies'}</span>
            </div>
          </div>
        </div>
      </WidgetErrorBoundary>
    </div>
  );
}

export default PoliciesList;

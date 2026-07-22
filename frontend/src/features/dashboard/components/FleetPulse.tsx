import { useState } from 'react';
import { useFleetOverview, useFleetHealth } from '../hooks/useDashboard';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/Card';
import { Skeleton } from '../../../components/ui/Skeleton';
import { AreaChart, Area, ResponsiveContainer, YAxis, Tooltip, CartesianGrid } from 'recharts';

function formatTime(val: string) {
  const d = new Date(val);
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
}

export function FleetPulse() {
  const { data: overview, isLoading: isOverviewLoading } = useFleetOverview();
  const { data: health, isLoading: isHealthLoading } = useFleetHealth();
  const [timeRange, setTimeRange] = useState('24h');

  const isLoading = isOverviewLoading || isHealthLoading;

  if (isLoading || !overview || !health) {
    return (
      <Card className="h-full min-h-[280px]">
        <CardHeader className="pb-2">
          <CardTitle>Fleet Pulse</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  // The backend doesn't currently expose a unified Fleet Health Score, Agent Uptime, or Avg Check-in.
  // We strictly display N/A or hide them per instructions.
  const fleetHealthScore = 'N/A';
  const avgCheckIn = 'N/A';
  const agentUptime = 'N/A';

  return (
    <Card className="h-full flex flex-col max-h-[340px]">
      <CardHeader className="pb-0 flex flex-row items-center justify-between shrink-0">
        <CardTitle>Fleet Pulse</CardTitle>
        <div className="flex bg-surface-secondary rounded-lg p-0.5 text-xs">
          {['24h', '7d', '30d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded-md transition-colors ${
                timeRange === range
                  ? 'bg-card text-text-primary shadow-sm font-medium'
                  : 'text-text-muted hover:text-text-primary'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col justify-between pt-4 pb-5 overflow-hidden">
        
        {/* Top Section: Score & Chart */}
        <div className="flex flex-col lg:flex-row gap-6 mb-4 flex-1 min-h-[120px]">
          <div className="flex flex-col justify-center min-w-[120px]">
            <span className="text-sm font-medium text-text-muted mb-1">Health Score</span>
            <div className="flex items-baseline gap-1">
              <span className="text-5xl font-bold text-text-primary tracking-tight">{fleetHealthScore}</span>
              <span className="text-sm text-text-muted font-medium">/100</span>
            </div>
          </div>
          
          <div className="flex-1 h-[100px] lg:h-full mt-2 lg:mt-0 min-h-[100px]" aria-label="Fleet CPU Load Trend">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={health} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--tw-colors-border)" opacity={0.5} />
                <YAxis hide domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--tw-colors-surface-secondary)', border: '1px solid var(--tw-colors-border)' }}
                  labelFormatter={formatTime}
                />
                <Area type="monotone" dataKey="cpu" name="Avg CPU %" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bottom Section: Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 pt-4 border-t border-border shrink-0">
          <div className="flex flex-col gap-2">
            <span className="text-xs text-text-muted">Online</span>
            <span className="text-sm font-semibold text-text-primary">{overview.online}</span>
          </div>
          <div className="flex flex-col gap-2">
            <span className="text-xs text-text-muted">Offline</span>
            <span className="text-sm font-semibold text-text-primary">{overview.offline}</span>
          </div>
          <div className="flex flex-col gap-2">
            <span className="text-xs text-text-muted">Critical Issues</span>
            <span className="text-sm font-semibold text-text-primary">{overview.criticalAlerts}</span>
          </div>
          <div className="flex flex-col gap-2">
            <span className="text-xs text-text-muted truncate">Avg Check-in</span>
            <span className="text-sm font-semibold text-text-primary">{avgCheckIn}</span>
          </div>
          <div className="flex flex-col gap-2">
            <span className="text-xs text-text-muted truncate">Agent Uptime</span>
            <span className="text-sm font-semibold text-text-primary">{agentUptime}</span>
          </div>
        </div>

      </CardContent>
    </Card>
  );
}

export default FleetPulse;

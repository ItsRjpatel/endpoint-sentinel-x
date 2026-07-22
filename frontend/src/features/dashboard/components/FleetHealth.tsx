import React from 'react';
import { useFleetHealth } from '../hooks/useDashboard';
import { HealthDataPoint } from '../types';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/Card';
import { Skeleton } from '../../../components/ui/Skeleton';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
  LineChart, Line
} from 'recharts';

function formatTime(val: string) {
  const d = new Date(val);
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
}

interface HealthChartProps {
  data: HealthDataPoint[];
  dataKey: string;
  color: string;
  name: string;
  type?: 'area' | 'line';
}

const HealthChart = React.memo(({ data, dataKey, color, name, type = 'area' }: HealthChartProps) => {
  return (
    <div className="h-[200px] w-full mt-4" role="img" aria-label={`${name} chart over time`}>
      <ResponsiveContainer width="100%" height="100%">
        {type === 'area' ? (
          <AreaChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--tw-colors-border)" opacity={0.5} />
            <XAxis dataKey="time" tickFormatter={formatTime} stroke="var(--tw-colors-text-muted)" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="var(--tw-colors-text-muted)" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: 'var(--tw-colors-surface-secondary)', border: '1px solid var(--tw-colors-border)' }}
              labelFormatter={formatTime}
            />
            <Area type="monotone" dataKey={dataKey} name={name} stroke={color} fill={color} fillOpacity={0.2} />
          </AreaChart>
        ) : (
          <LineChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--tw-colors-border)" opacity={0.5} />
            <XAxis dataKey="time" tickFormatter={formatTime} stroke="var(--tw-colors-text-muted)" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="var(--tw-colors-text-muted)" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: 'var(--tw-colors-surface-secondary)', border: '1px solid var(--tw-colors-border)' }}
              labelFormatter={formatTime}
            />
            <Line type="monotone" dataKey={dataKey} name={name} stroke={color} strokeWidth={2} dot={false} />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
});

export function FleetHealth() {
  const { data, isLoading } = useFleetHealth();

  if (isLoading || !data) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle>System Health Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" aria-busy="true" aria-live="polite">
            <Skeleton className="h-[200px] w-full" />
            <Skeleton className="h-[200px] w-full" />
            <Skeleton className="h-[200px] w-full" />
            <Skeleton className="h-[200px] w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Fleet Health & Performance</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-text-muted">CPU Usage Distribution</h4>
            <HealthChart data={data} dataKey="cpu" name="CPU %" color="#3b82f6" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-text-muted">Memory Usage Distribution</h4>
            <HealthChart data={data} dataKey="memory" name="Memory %" color="#8b5cf6" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-text-muted">Disk Usage</h4>
            <HealthChart data={data} dataKey="disk" name="Disk %" color="#10b981" type="line" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-text-muted">Network Traffic (KB/s)</h4>
            <HealthChart data={data} dataKey="networkIn" name="Network In" color="#f59e0b" type="line" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
export default FleetHealth;

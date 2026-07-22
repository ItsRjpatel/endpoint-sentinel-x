import React from 'react';
import { Activity } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../../components/ui/Card';
import { EndpointDetails } from '../../types';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
} from 'recharts';

function formatTime(val: string) {
  const d = new Date(val);
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
}

interface PerformanceChartProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any[];
  dataKey: string;
  color: string;
  name: string;
  type?: 'area' | 'line';
}

const PerformanceChart = React.memo(({ data, dataKey, color, name, type = 'area' }: PerformanceChartProps) => (
  <div className="h-[160px] w-full" role="img" aria-label={`${name} chart over time`}>
    <ResponsiveContainer width="100%" height="100%">
      {type === 'area' ? (
        <AreaChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#94a3b8" opacity={0.15} />
          <XAxis dataKey="time" tickFormatter={formatTime} stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} width={32} />
          <Tooltip
            contentStyle={{ backgroundColor: 'var(--card, #fff)', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 12 }}
            labelFormatter={formatTime}
          />
          <Area type="monotone" dataKey={dataKey} name={name} stroke={color} fill={color} fillOpacity={0.15} strokeWidth={2} />
        </AreaChart>
      ) : (
        <LineChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#94a3b8" opacity={0.15} />
          <XAxis dataKey="time" tickFormatter={formatTime} stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} width={32} />
          <Tooltip
            contentStyle={{ backgroundColor: 'var(--card, #fff)', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 12 }}
            labelFormatter={formatTime}
          />
          <Line type="monotone" dataKey={dataKey} name={name} stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      )}
    </ResponsiveContainer>
  </div>
));
PerformanceChart.displayName = 'PerformanceChart';

function MetricHeader({ label, value, unit = '%' }: { label: string; value: number; unit?: string }) {
  return (
    <div className="flex items-baseline justify-between">
      <h4 className="text-sm font-medium text-text-secondary">{label}</h4>
      <span className="text-sm font-bold tabular-nums text-text-primary">
        {value}
        {unit}
      </span>
    </div>
  );
}

interface PerformanceSectionProps {
  endpoint: EndpointDetails;
}

export function PerformanceSection({ endpoint }: PerformanceSectionProps) {
  const data = endpoint.performance.history;

  return (
    <Card>
      <CardHeader className="pb-3 border-b border-border">
        <CardTitle className="text-base flex items-center gap-2">
          <Activity className="h-4 w-4 text-text-muted" aria-hidden="true" />
          System Performance
          <span className="ml-auto text-xs font-normal text-text-muted">Last 24 hours</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-5">
        <div className="grid grid-cols-1 gap-x-8 gap-y-6 sm:grid-cols-2">
          <div>
            <MetricHeader label="CPU usage" value={endpoint.performance.currentCpuUsage} />
            <PerformanceChart data={data} dataKey="cpu" name="CPU %" color="#3b82f6" />
          </div>
          <div>
            <MetricHeader label="Memory usage" value={endpoint.performance.currentRamUsage} />
            <PerformanceChart data={data} dataKey="memory" name="Memory %" color="#8b5cf6" />
          </div>
          <div>
            <MetricHeader label="Disk active time" value={endpoint.performance.currentDiskUsage} />
            <PerformanceChart data={data} dataKey="disk" name="Disk %" color="#10b981" type="line" />
          </div>
          <div>
            <MetricHeader label="Network throughput" value={data[data.length - 1]?.networkIn ?? 0} unit=" KB/s" />
            <PerformanceChart data={data} dataKey="networkIn" name="Network in" color="#f59e0b" type="line" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

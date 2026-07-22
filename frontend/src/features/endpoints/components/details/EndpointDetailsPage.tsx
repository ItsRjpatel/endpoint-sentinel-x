import { useState } from 'react';
import { Cpu, HardDrive, Network as NetworkIcon, Package, Download, Settings, Users as UsersIcon, Activity } from 'lucide-react';
import { Card } from '../../../../components/ui/Card';
import { Skeleton } from '../../../../components/ui/Skeleton';
import { EndpointDetails } from '../../types';
import { EndpointDetailsHeader } from './EndpointDetailsHeader';
import { DeviceSummary } from './DeviceSummary';
import { SecuritySection } from './SecuritySection';
import { RiskScoreCard } from './RiskScoreCard';
import { PerformanceSection } from './PerformanceSection';
import { HardwareTab } from './HardwareTab';
import { StorageTab } from './StorageTab';
import { NetworkTab } from './NetworkTab';
import { SoftwareTab } from './SoftwareTab';
import { UpdatesTab } from './UpdatesTab';
import { ServicesTab } from './ServicesTab';
import { UsersTab } from './UsersTab';
import { ActivityTimeline } from './ActivityTimeline';

const TABS = [
  { id: 'hardware', label: 'Hardware', icon: Cpu },
  { id: 'storage', label: 'Storage', icon: HardDrive },
  { id: 'network', label: 'Network', icon: NetworkIcon },
  { id: 'software', label: 'Software', icon: Package },
  { id: 'updates', label: 'Updates', icon: Download },
  { id: 'services', label: 'Services', icon: Settings },
  { id: 'users', label: 'Users', icon: UsersIcon },
  { id: 'activity', label: 'Activity', icon: Activity },
] as const;

type TabId = (typeof TABS)[number]['id'];

interface EndpointDetailsPageProps {
  /** Fully-resolved endpoint record. Fetch this with your own data layer
   *  (e.g. useEndpointDetails / useEndpointDetailsWebSocket) and pass it in —
   *  this component renders only. */
  endpoint?: EndpointDetails;
  isLoading?: boolean;
}

function EndpointDetailsSkeleton() {
  return (
    <div className="mx-auto max-w-[1600px] space-y-6 p-4 sm:p-6">
      <Skeleton className="h-4 w-40" />
      <Skeleton className="h-28 w-full rounded-xl" />
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Skeleton className="h-64 w-full rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
      <Skeleton className="h-80 w-full rounded-xl" />
      <Skeleton className="h-96 w-full rounded-xl" />
    </div>
  );
}

export function EndpointDetailsPage({ endpoint, isLoading }: EndpointDetailsPageProps) {
  const [activeTab, setActiveTab] = useState<TabId>('hardware');

  if (isLoading || !endpoint) {
    return <EndpointDetailsSkeleton />;
  }

  return (
    <div className="mx-auto max-w-[1600px] space-y-6 p-4 sm:p-6">
      <EndpointDetailsHeader endpoint={endpoint} />

      {/* Triage row — risk, identity, and posture at a glance */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <RiskScoreCard endpoint={endpoint} />
        <DeviceSummary endpoint={endpoint} />
        <SecuritySection endpoint={endpoint} />
      </div>

      <PerformanceSection endpoint={endpoint} />

      {/* Deep-dive tabs */}
      <Card className="overflow-hidden">
        <div className="hide-scrollbar flex overflow-x-auto border-b border-border bg-surface-primary">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex shrink-0 items-center gap-2 border-b-2 px-4 py-3.5 text-sm font-medium whitespace-nowrap transition-colors ${
                  active
                    ? 'border-primary text-primary bg-primary/5'
                    : 'border-transparent text-text-muted hover:text-text-primary hover:bg-surface-secondary/60'
                }`}
                aria-selected={active}
                role="tab"
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="p-5 sm:p-6 min-h-[500px]" role="tabpanel">
          {activeTab === 'hardware' && <HardwareTab endpoint={endpoint} />}
          {activeTab === 'storage' && <StorageTab endpoint={endpoint} />}
          {activeTab === 'network' && <NetworkTab endpoint={endpoint} />}
          {activeTab === 'software' && <SoftwareTab endpoint={endpoint} />}
          {activeTab === 'updates' && <UpdatesTab endpoint={endpoint} />}
          {activeTab === 'services' && <ServicesTab endpoint={endpoint} />}
          {activeTab === 'users' && <UsersTab endpoint={endpoint} />}
          {activeTab === 'activity' && <ActivityTimeline endpoint={endpoint} />}
        </div>
      </Card>
    </div>
  );
}

export default EndpointDetailsPage;

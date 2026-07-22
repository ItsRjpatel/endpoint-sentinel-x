import { Endpoint, EndpointFilters, EndpointListResponse, EndpointPagination, EndpointSort } from '../types';
import { EndpointRepository } from './EndpointRepository';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const generateMockEndpoints = (): Endpoint[] => {
  const endpoints: Endpoint[] = [];
  const osList = ['Windows 10', 'Windows 11', 'Windows Server 2022', 'Windows Server 2019', 'macOS Sonoma', 'Ubuntu 22.04'];
  const users = ['admin@corp.local', 'jdoe@corp.local', 'jsmith@corp.local', null, 'svc_account@corp.local'];
  
  for (let i = 1; i <= 150; i++) {
    const isServer = i <= 30;
    const type = isServer ? 'server' : (i % 2 === 0 ? 'desktop' : 'laptop');
    const os = isServer ? osList[2 + (i % 2)] : osList[i % 2];
    
    let status: 'online' | 'offline' | 'inactive' = 'online';
    if (i % 7 === 0) status = 'offline';
    if (i % 15 === 0) status = 'inactive';

    let compliance: 'compliant' | 'non-compliant' | 'unknown' = 'compliant';
    if (i % 11 === 0) compliance = 'non-compliant';
    if (i % 19 === 0) compliance = 'unknown';

    endpoints.push({
      id: `ep-${i.toString().padStart(4, '0')}`,
      hostname: isServer ? `SRV-${i.toString().padStart(3, '0')}` : `WS-${i.toString().padStart(4, '0')}`,
      status,
      deviceType: type,
      user: isServer ? null : users[i % users.length],
      os,
      ipAddress: `10.0.${Math.floor(i / 255)}.${i % 255}`,
      securityScore: 100 - (i % 40),
      compliance,
      lastSeen: new Date(Date.now() - (i * 1000 * 60)).toISOString(),
      alerts: i % 10 === 0 ? Math.floor(i / 10) : 0,
    });
  }
  return endpoints;
};

const MOCK_DATA = generateMockEndpoints();

export class EndpointMockRepository implements EndpointRepository {
  async getEndpoints(
    filters: EndpointFilters,
    sort: EndpointSort,
    pagination: EndpointPagination
  ): Promise<EndpointListResponse> {
    await delay(300); // simulate network latency

    let filtered = [...MOCK_DATA];

    // Search
    if (filters.search) {
      const q = filters.search.toLowerCase();
      filtered = filtered.filter(ep => 
        ep.hostname.toLowerCase().includes(q) ||
        ep.user?.toLowerCase().includes(q) ||
        ep.ipAddress.includes(q)
      );
    }

    // Exact matches
    if (filters.status && filters.status !== 'all') {
      filtered = filtered.filter(ep => ep.status === filters.status);
    }
    if (filters.deviceType && filters.deviceType !== 'all') {
      filtered = filtered.filter(ep => ep.deviceType === filters.deviceType);
    }
    if (filters.os && filters.os !== 'all') {
      filtered = filtered.filter(ep => ep.os === filters.os);
    }
    if (filters.compliance && filters.compliance !== 'all') {
      filtered = filtered.filter(ep => ep.compliance === filters.compliance);
    }

    // Security Logic
    if (filters.security && filters.security !== 'all') {
      filtered = filtered.filter(ep => {
        if (filters.security === 'protected') return ep.securityScore >= 80;
        if (filters.security === 'atRisk') return ep.securityScore >= 60 && ep.securityScore < 80;
        if (filters.security === 'critical') return ep.securityScore < 60;
        return true;
      });
    }

    // Alerts Logic
    if (filters.alerts && filters.alerts !== 'all') {
      if (filters.alerts === 'hasAlerts') {
        filtered = filtered.filter(ep => ep.alerts > 0);
      } else if (filters.alerts === 'criticalAlerts') {
        filtered = filtered.filter(ep => ep.alerts > 3);
      }
    }

    // Sort
    filtered.sort((a, b) => {
      const aVal = a[sort.field];
      const bVal = b[sort.field];
      
      if (aVal === null) return 1;
      if (bVal === null) return -1;

      if (aVal < bVal) return sort.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sort.direction === 'asc' ? 1 : -1;
      return 0;
    });

    // Pagination
    const start = (pagination.page - 1) * pagination.pageSize;
    const end = start + pagination.pageSize;
    const paginated = filtered.slice(start, end);

    return {
      data: paginated,
      total: filtered.length
    };
  }
}

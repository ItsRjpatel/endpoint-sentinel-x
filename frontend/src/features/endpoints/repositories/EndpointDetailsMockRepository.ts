import { EndpointDetails } from '../types';
import { EndpointDetailsRepository } from './EndpointDetailsRepository';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const generateMockDetails = (id: string): EndpointDetails => {
  return {
    id,
    status: 'online',
    hostname: id.startsWith('ep-') ? `WS-${id.split('-')[1]}` : `WS-1042`,
    deviceType: 'laptop',
    user: 'jdoe@corp.local',
    os: 'Windows 11',
    ipAddress: '10.0.1.42',
    securityScore: 92,
    compliance: 'compliant',
    lastSeen: new Date().toISOString(),
    alerts: 0,

    manufacturer: 'Lenovo',
    model: 'ThinkPad T14 Gen 3',
    serialNumber: 'PF3K92A1',
    assetTag: 'AST-84920',
    domain: 'corp.local',
    macAddress: '00:1A:2B:3C:4D:5E',

    operatingSystem: {
      name: 'Windows 11 Enterprise',
      version: '22H2',
      build: '22621.1702',
      architecture: '64-bit',
      installDate: '2023-01-15T08:30:00Z'
    },

    hardware: {
      cpu: 'Intel Core i7-1260P',
      cpuCores: 12,
      ramTotalGB: 32,
      motherboard: 'LENOVO 21AHS00Y00',
      biosVersion: 'N3BET54W (1.32 )',
      graphics: 'Intel Iris Xe Graphics',
      storageDevices: [
        {
          driveLetter: 'C:',
          fileSystem: 'NTFS',
          totalSpaceGB: 512,
          usedSpaceGB: 180,
          freeSpaceGB: 332,
          healthStatus: 'Healthy'
        }
      ]
    },

    performance: {
      currentCpuUsage: 14,
      currentRamUsage: 45,
      currentDiskUsage: 2,
      history: Array.from({ length: 24 }).map((_, i) => ({
        time: new Date(Date.now() - (23 - i) * 1000 * 60 * 60).toISOString(),
        cpu: Math.floor(Math.random() * 40) + 10,
        memory: Math.floor(Math.random() * 30) + 30,
        disk: Math.floor(Math.random() * 10) + 1,
        networkIn: Math.floor(Math.random() * 2000),
        networkOut: Math.floor(Math.random() * 1000)
      }))
    },

    security: {
      firewallEnabled: true,
      defenderActive: true,
      bitlockerEnabled: true,
      secureBootEnabled: true,
      tpmPresent: true,
      tpmVersion: '2.0',
      realTimeProtection: true
    },

    networkAdapters: [
      {
        id: 'eth0',
        name: 'Intel(R) Ethernet Connection (14) I219-V',
        ipv4: '10.0.1.42',
        mac: '00:1A:2B:3C:4D:5E',
        gateway: '10.0.1.1',
        dns: ['10.0.0.53', '10.0.0.54'],
        dhcpEnabled: true
      },
      {
        id: 'wlan0',
        name: 'Intel(R) Wi-Fi 6E AX211 160MHz',
        ipv4: '192.168.1.105',
        mac: 'A0:B1:C2:D3:E4:F5',
        gateway: '192.168.1.1',
        dns: ['8.8.8.8'],
        dhcpEnabled: true
      }
    ],

    software: [
      { id: '1', name: 'Microsoft Office 365 Apps', version: '16.0.16327.20214', publisher: 'Microsoft Corporation', installDate: '2023-01-15T09:00:00Z' },
      { id: '2', name: 'Google Chrome', version: '114.0.5735.199', publisher: 'Google LLC', installDate: '2023-02-10T11:20:00Z' },
      { id: '3', name: 'Visual Studio Code', version: '1.80.0', publisher: 'Microsoft Corporation', installDate: '2023-03-05T14:15:00Z' },
    ],

    updates: [
      { kbNumber: 'KB5027231', title: '2023-06 Cumulative Update for Windows 11', installedDate: '2023-06-15T02:00:00Z', status: 'Installed' },
      { kbNumber: 'KB5027397', title: '2023-06 Cumulative Update for .NET Framework', installedDate: '2023-06-15T02:05:00Z', status: 'Installed' },
      { kbNumber: 'KB5028185', title: '2023-07 Cumulative Update Preview', installedDate: '', status: 'Pending' },
    ],

    services: [
      { name: 'WinDefend', displayName: 'Microsoft Defender Antivirus Service', status: 'Running', startupType: 'Automatic' },
      { name: 'wuauserv', displayName: 'Windows Update', status: 'Running', startupType: 'Automatic' },
      { name: 'Spooler', displayName: 'Print Spooler', status: 'Running', startupType: 'Automatic' },
      { name: 'mpssvc', displayName: 'Windows Defender Firewall', status: 'Running', startupType: 'Automatic' },
    ],

    users: [
      { username: 'jdoe', enabled: true, administrator: false, lastLogin: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() },
      { username: 'local_admin', enabled: true, administrator: true, lastLogin: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString() },
      { username: 'Guest', enabled: false, administrator: false, lastLogin: null },
    ],

    timeline: [
      { id: 't1', type: 'User Login', message: 'User jdoe logged in', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), severity: 'info' },
      { id: 't2', type: 'Agent Connected', message: 'Sentinel Agent established connection', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2 - 5000).toISOString(), severity: 'success' },
      { id: 't3', type: 'Windows Update', message: 'KB5027231 installed successfully', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(), severity: 'info' },
      { id: 't4', type: 'Alert Created', message: 'Failed login attempt (Administrator)', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(), severity: 'warning' },
    ]
  };
};

export class EndpointDetailsMockRepository implements EndpointDetailsRepository {
  async getEndpointDetails(id: string): Promise<EndpointDetails> {
    await delay(600);
    return generateMockDetails(id);
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars, @typescript-eslint/no-explicit-any
  async getHistoricalPerformance(_id: string, _timeRange: string): Promise<any> {
    await delay(600);
    return [];
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async refreshEndpoint(_id: string): Promise<void> {
    await delay(800);
    // In a real app this would trigger the backend to fetch fresh data from the agent
  }
}

import { EndpointDetails } from '../../types';

export const MOCK_ENDPOINT: EndpointDetails = {
  id: 'ep-7a29b431',
  hostname: 'LPT-ENG-JW',
  deviceType: 'laptop',
  status: 'online',
  isolated: false,
  lastSeen: new Date().toISOString(),
  user: 'j.wright',
  domain: 'corp.sentinelx.io',
  manufacturer: 'Lenovo',
  model: 'ThinkPad T14 Gen 3',
  serialNumber: 'PF3M921D',
  assetTag: 'AST-882190',
  ipAddress: '10.4.55.102',
  macAddress: '00:1A:2B:3C:4D:5E',
  compliance: 'compliant',
  securityScore: 82,
  alerts: 2,
  openAlertsCount: 2,
  os: 'Windows 11',
  operatingSystem: {
    name: 'Windows 11 Enterprise',
    version: '23H2',
    build: '22631.3296',
    architecture: 'x64',
    installDate: new Date().toISOString(),
  },

  riskScore: 68,
  riskLevel: 'high',
  riskFactors: [
    { label: 'Outdated antivirus signatures', weight: 'high' },
    { label: 'Suspicious PowerShell script executed', weight: 'high' },
    { label: 'Pending critical OS update', weight: 'medium' },
  ],

  security: {
    firewallEnabled: true,
    defenderActive: true,
    realTimeProtection: true,
    bitlockerEnabled: true,
    secureBootEnabled: true,
    tpmPresent: true,
    tpmVersion: '2.0',
  },

  performance: {
    currentCpuUsage: 45,
    currentRamUsage: 82,
    currentDiskUsage: 12,
    history: Array.from({ length: 24 }).map((_, i) => {
      const d = new Date();
      d.setHours(d.getHours() - (23 - i));
      return {
        time: d.toISOString(),
        cpu: Math.floor(20 + Math.random() * 40),
        memory: Math.floor(60 + Math.random() * 30),
        disk: Math.floor(5 + Math.random() * 20),
        networkIn: Math.floor(50 + Math.random() * 500),
        networkOut: Math.floor(20 + Math.random() * 200),
      };
    }),
  },

  hardware: {
    cpu: '12th Gen Intel Core i7-1260P',
    cpuCores: 12,
    ramTotalGB: 32,
    motherboard: 'LENOVO 21AHS00Y00',
    biosVersion: 'N3BET54W (1.32)',
    graphics: 'Intel Iris Xe Graphics',
    storageDevices: [
      {
        driveLetter: 'C:',
        fileSystem: 'NTFS',
        totalSpaceGB: 512,
        usedSpaceGB: 412,
        freeSpaceGB: 100,
        healthStatus: 'Healthy',
      },
      {
        driveLetter: 'D:',
        fileSystem: 'NTFS',
        totalSpaceGB: 1024,
        usedSpaceGB: 950,
        freeSpaceGB: 74,
        healthStatus: 'Warning',
      },
    ],
  },

  networkAdapters: [
    {
      id: 'net-1',
      name: 'Intel(R) Wi-Fi 6E AX211 160MHz',
      connectionType: 'Wi-Fi',
      ipv4: '10.4.55.102',
      mac: '00:1A:2B:3C:4D:5E',
      gateway: '10.4.55.1',
      dns: ['10.0.0.11', '10.0.0.12'],
      dhcpEnabled: true,
    },
    {
      id: 'net-2',
      name: 'Cisco AnyConnect Secure Mobility Client Virtual Miniport',
      connectionType: 'VPN',
      ipv4: '172.16.8.44',
      mac: '00:05:9A:3C:7A:00',
      gateway: '172.16.8.1',
      dns: ['172.16.0.10'],
      dhcpEnabled: true,
    },
  ],

  software: [
    { id: 'sw-1', name: 'Microsoft Office 365 ProPlus', version: '16.0.14326', publisher: 'Microsoft', installDate: '2023-01-15' },
    { id: 'sw-2', name: 'Slack', version: '4.36.138', publisher: 'Slack Technologies', installDate: '2023-10-12' },
    { id: 'sw-3', name: 'Docker Desktop', version: '4.26.1', publisher: 'Docker Inc.', installDate: '2023-12-05' },
    { id: 'sw-4', name: 'Visual Studio Code', version: '1.85.2', publisher: 'Microsoft', installDate: '2024-01-20' },
  ],

  updates: [
    { kbNumber: 'KB5040442', title: 'Cumulative Update for Windows 11 23H2', installedDate: '2024-07-14', status: 'Installed' },
    { kbNumber: 'KB5039562', title: '.NET Framework Security and Quality Rollup', installedDate: '', status: 'Pending' },
    { kbNumber: 'KB5037853', title: 'Servicing Stack Update', installedDate: '2024-05-18', status: 'Installed' },
    { kbNumber: 'KB5041234', title: 'Optional Preview Update', installedDate: '', status: 'Failed' },
  ],

  services: [
    { name: 'WinDefend', displayName: 'Microsoft Defender Antivirus Service', status: 'Running', startupType: 'Automatic' },
    { name: 'wuauserv', displayName: 'Windows Update', status: 'Running', startupType: 'Automatic' },
    { name: 'Spooler', displayName: 'Print Spooler', status: 'Stopped', startupType: 'Manual' },
    { name: 'RemoteRegistry', displayName: 'Remote Registry', status: 'Stopped', startupType: 'Disabled' },
  ],

  users: [
    { username: 'priya.sharma', enabled: true, administrator: false, lastLogin: new Date().toISOString() },
    { username: 'contoso\\admin-jsmith', enabled: true, administrator: true, lastLogin: '2024-07-15T10:22:00Z' },
    { username: 'svc-backup', enabled: false, administrator: false, lastLogin: null },
  ],

  timeline: [
    { id: 'ev-1', type: 'Alert Created', severity: 'error', message: 'Suspicious PowerShell command line detected — encoded command execution.', timestamp: new Date().toISOString() },
    { id: 'ev-2', type: 'Policy Applied', severity: 'success', message: 'Endpoint Protection Baseline profile applied successfully.', timestamp: '2024-07-20T18:10:00Z' },
    { id: 'ev-3', type: 'User Login', severity: 'info', message: 'priya.sharma signed in interactively.', timestamp: '2024-07-20T09:02:00Z' },
    { id: 'ev-4', type: 'Windows Update', severity: 'success', message: 'KB5040442 installed and pending restart.', timestamp: '2024-07-19T22:41:00Z' },
  ],
};

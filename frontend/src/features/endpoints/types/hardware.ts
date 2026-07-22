export interface DiskInfo {
  driveLetter: string;
  fileSystem: string;
  totalSpaceGB: number;
  usedSpaceGB: number;
  freeSpaceGB: number;
  healthStatus: 'Healthy' | 'Warning' | 'Critical';
}

export interface HardwareInfo {
  cpu: string;
  cpuCores: number;
  ramTotalGB: number;
  motherboard: string;
  biosVersion: string;
  graphics: string;
  storageDevices: DiskInfo[];
}

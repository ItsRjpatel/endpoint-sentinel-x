export interface PerformanceDataPoint {
  time: string;
  cpu: number;
  memory: number;
  disk: number;
  networkIn: number;
  networkOut: number;
}

export interface PerformanceInfo {
  currentCpuUsage: number;
  currentRamUsage: number;
  currentDiskUsage: number;
  history: PerformanceDataPoint[];
}

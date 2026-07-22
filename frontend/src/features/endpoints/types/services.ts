export interface WindowsService {
  name: string;
  displayName: string;
  status: 'Running' | 'Stopped' | 'Paused' | 'Unknown';
  startupType: 'Automatic' | 'Manual' | 'Disabled';
}

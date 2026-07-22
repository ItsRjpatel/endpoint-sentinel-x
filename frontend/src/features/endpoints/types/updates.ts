export interface WindowsUpdate {
  kbNumber: string;
  title: string;
  installedDate: string;
  status: 'Installed' | 'Pending' | 'Failed';
}

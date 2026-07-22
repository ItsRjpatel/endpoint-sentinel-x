export interface SecurityInfo {
  firewallEnabled: boolean;
  defenderActive: boolean;
  bitlockerEnabled: boolean;
  secureBootEnabled: boolean;
  tpmPresent: boolean;
  tpmVersion: string | null;
  realTimeProtection: boolean;
}

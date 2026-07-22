export interface NetworkAdapter {
  id: string;
  name: string;
  ipv4: string;
  mac: string;
  gateway: string;
  dns: string[];
  dhcpEnabled: boolean;
  connectionType?: 'Ethernet' | 'Wi-Fi' | 'VPN';
}

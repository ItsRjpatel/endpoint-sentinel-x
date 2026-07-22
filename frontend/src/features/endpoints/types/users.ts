export interface LocalUser {
  username: string;
  enabled: boolean;
  administrator: boolean;
  lastLogin: string | null;
}

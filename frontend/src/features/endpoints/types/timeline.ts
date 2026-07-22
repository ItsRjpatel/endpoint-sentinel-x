export type TimelineEventType = 
  | 'Agent Connected' 
  | 'Agent Disconnected' 
  | 'Alert Created' 
  | 'Policy Applied' 
  | 'Software Installed' 
  | 'Windows Update' 
  | 'User Login' 
  | 'Restart' 
  | 'Shutdown' 
  | 'Command Executed'
  | 'Isolation';

export interface TimelineEvent {
  id: string;
  type: TimelineEventType;
  message: string;
  timestamp: string;
  severity: 'info' | 'warning' | 'error' | 'success';
}

export interface EndpointCommand {
  id: string;
  command: string;
  status: 'pending' | 'completed' | 'failed';
  executedAt: string;
  executedBy: string;
}

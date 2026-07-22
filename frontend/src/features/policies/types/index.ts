export interface PolicyVersion {
  id: number;
  uuid: string;
  policy_id: number;
  version: number;
  configuration: Record<string, unknown>;
  change_summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface PolicyAssignment {
  id: number;
  uuid: string;
  policy_id: number;
  endpoint_id: number;
  assigned_by_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface Policy {
  id: number;
  uuid: string;
  organization_id: number;
  name: string;
  description: string | null;
  category: string;
  enabled: boolean;
  priority: number;
  current_version: number;
  created_by_id: number | null;
  created_at: string;
  updated_at: string;
  versions?: PolicyVersion[];
  assignments?: PolicyAssignment[];
}

export interface PolicyCreate {
  name: string;
  description?: string;
  category: string;
  enabled?: boolean;
  priority?: number;
  configuration: Record<string, unknown>;
}

export interface PolicyUpdate {
  name?: string;
  description?: string;
  category?: string;
  enabled?: boolean;
  priority?: number;
  configuration?: Record<string, unknown>;
  change_summary?: string;
}

export interface PolicyAssignmentCreate {
  endpoint_id: number;
}

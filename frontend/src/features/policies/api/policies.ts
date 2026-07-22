import { apiClient } from "@/api/client";
import {
  Policy,
  PolicyAssignment,
  PolicyAssignmentCreate,
  PolicyCreate,
  PolicyUpdate,
} from "../types";

export const getPolicies = () => {
  return apiClient.get<Policy[]>("/policies");
};

export const getPolicy = (id: number) => {
  return apiClient.get<Policy>(`/policies/${id}`);
};

export const createPolicy = (data: PolicyCreate) => {
  return apiClient.post<Policy>("/policies", data);
};

export const updatePolicy = (id: number, data: PolicyUpdate) => {
  return apiClient.put<Policy>(`/policies/${id}`, data);
};

export const deletePolicy = (id: number) => {
  return apiClient.delete<void>(`/policies/${id}`);
};

export const assignPolicy = (id: number, data: PolicyAssignmentCreate) => {
  return apiClient.post<PolicyAssignment>(`/policies/${id}/assign`, data);
};

export const unassignPolicy = (id: number, endpointId: number) => {
  return apiClient.delete<void>(`/policies/${id}/assign/${endpointId}`);
};

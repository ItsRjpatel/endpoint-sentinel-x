import { useQuery } from "@tanstack/react-query";
import { getPolicies, getPolicy } from "../api/policies";
import { Policy } from "../types";

export const usePolicies = () => {
  return useQuery<Policy[]>({
    queryKey: ["policies"],
    queryFn: getPolicies,
  });
};

export const usePolicy = (id: number) => {
  return useQuery<Policy>({
    queryKey: ["policies", id],
    queryFn: () => getPolicy(id),
    enabled: !!id,
  });
};

// app/lib/api.ts

import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api/payments";


const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types
export interface Merchant {
  id: string;
  name: string;
  settlement_account: string;
  created_at: string;
  total_payments?: number;
  total_revenue?: string;
}

export interface Payment {
  id: string;
  merchant: string;
  merchant_name?: string;
  amount: string;
  method: "MPESA" | "CARD" | "BANK";
  status: "SUCCESS" | "FAILED" | "PENDING";
  created_at: string;
}

export interface Fee {
  method: "MPESA" | "CARD" | "BANK";
  percentage: string;
}

export interface Settlement {
  id: string;
  merchant: string;
  merchant_name?: string;
  gross_amount: string;
  fee_amount: string;
  net_amount: string;
  created_at: string;
}

export interface MerchantSummary {
  merchant: string;
  total_payments: number;
  successful_payments: number;
  failed_payments: number;
  pending_payments: number;
  total_amount: string;
  settlements: Settlement[];
}

// API functions
export const merchantsAPI = {
  list: () => apiClient.get<{ results: Merchant[] }>("/merchants/"),
  create: (data: { name: string; settlement_account: string }) =>
    apiClient.post<Merchant>("/merchants/", data),
  get: (id: string) => apiClient.get<Merchant>(`/merchants/${id}/`),
  update: (id: string, data: Partial<Merchant>) =>
    apiClient.put<Merchant>(`/merchants/${id}/`, data),
  delete: (id: string) => apiClient.delete(`/merchants/${id}/`),
  summary: (id: string) =>
    apiClient.get<MerchantSummary>(`/merchants/${id}/summary/`),
};

export const paymentsAPI = {
  list: (params?: { merchant_id?: string; status?: string }) =>
    apiClient.get<{ results: Payment[] }>("/payments/", { params }),
  create: (data: { merchant: string; amount: string; method: string }) =>
    apiClient.post<Payment>("/payments/", data),
  get: (id: string) => apiClient.get<Payment>(`/payments/${id}/`),
  updateStatus: (id: string, status: string) =>
    apiClient.patch<Payment>(`/payments/${id}/update_status/`, { status }),
};

export const feesAPI = {
  list: () => apiClient.get<Fee[]>("/fees/"),
  create: (data: Fee) => apiClient.post<Fee>("/fees/", data),
  update: (method: string, data: { percentage: string }) =>
    apiClient.put<Fee>(`/fees/${method}/`, data),
};

export const settlementsAPI = {
  list: (params?: { merchant_id?: string }) =>
    apiClient.get<{ results: Settlement[] }>("/settlements/", { params }),
  get: (id: string) => apiClient.get<Settlement>(`/settlements/${id}/`),
  processAll: () => apiClient.post("/settlements/process/"),
  processMerchant: (merchantId: string) =>
    apiClient.post(`/settlements/process/${merchantId}/`),
};

export default apiClient;

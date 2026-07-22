const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

type FetchOptions = RequestInit & {
  // custom options can go here
};

class ApiClient {
  private tokenProvider: (() => string | null) | null = null;

  setTokenProvider(provider: () => string | null) {
    this.tokenProvider = provider;
  }

  private async request<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { headers: customHeaders, ...restOptions } = options;
    
    const headers = new Headers(customHeaders);
    headers.set("Content-Type", "application/json");

    if (this.tokenProvider) {
      const token = this.tokenProvider();
      if (token) {
        headers.set("Authorization", `Bearer ${token}`);
      }
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers,
      ...restOptions,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.error || `HTTP Error ${response.status}`);
    }

    // Check if the response is empty before trying to parse JSON
    const text = await response.text();
    if (!text) {
      return {} as T;
    }

    return JSON.parse(text) as T;
  }

  get<T>(endpoint: string, options?: FetchOptions) {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  post<T>(endpoint: string, body: unknown, options?: FetchOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  put<T>(endpoint: string, body: unknown, options?: FetchOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(body),
    });
  }

  delete<T>(endpoint: string, options?: FetchOptions) {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }
}

export const apiClient = new ApiClient();

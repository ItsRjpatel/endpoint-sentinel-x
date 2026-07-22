const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1";

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
    if (!headers.has("Content-Type") && !(restOptions.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }

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
    const serializedBody =
      body instanceof FormData || body instanceof URLSearchParams || typeof body === "string"
        ? body
        : JSON.stringify(body);

    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: serializedBody,
    });
  }

  put<T>(endpoint: string, body: unknown, options?: FetchOptions) {
    const serializedBody =
      body instanceof FormData || body instanceof URLSearchParams || typeof body === "string"
        ? body
        : JSON.stringify(body);

    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: serializedBody,
    });
  }

  delete<T>(endpoint: string, options?: FetchOptions) {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }
}

export const apiClient = new ApiClient();

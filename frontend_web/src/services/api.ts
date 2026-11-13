export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "https://agribrain-35zr.onrender.com";

export interface ApiError extends Error {
  status?: number;
  retryable?: boolean;
}

export class ApiService {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${BACKEND_URL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error: ApiError = new Error(
          `API Error: ${response.status} ${response.statusText}`
        );
        error.status = response.status;
        error.retryable = response.status >= 500 || response.status === 429;
        throw error;
      }

      return await response.json();
    } catch (err) {
      clearTimeout(timeoutId);
      if (err instanceof Error && err.name === "AbortError") {
        const error: ApiError = new Error("Request timeout - please try again");
        error.retryable = true;
        throw error;
      }
      throw err;
    }
  }

  static async sendChatMessage(
    message: string,
    context?: {
      is_context_aware?: boolean;
      coordinates?: { lat: number; lon: number };
      soilParams?: { ph: number; texture: string; organic_carbon: number; n: number; p: number; k: number };
      annualRainfall?: number;
      selectedCrop?: string | null;
      farmParams?: any;
      simulationResults?: any;
      calendarStages?: any[];
    }
  ) {
    return this.request<{ response: string }>("/api/v1/chat/troubleshoot", {
      method: "POST",
      body: JSON.stringify({
        session_id: "agribrain_chat",
        user_question: message,
        context: context?.is_context_aware ? context : undefined,
      }),
    });
  }

  static async getCropRecommendations(params: {
    district_id: number;
    soil_type: string;
    rainfall_mm: number;
    temperature_c?: number;
    humidity_percent?: number;
    ph?: number;
    n?: number;
    p?: number;
    k?: number;
    top_k?: number;
  }) {
    return this.request<{ recommendations: any[] }>("/api/v1/crop/recommend", {
      method: "POST",
      body: JSON.stringify({ ...params, top_k: params.top_k || 5 }),
    });
  }

  static async runSimulation(params: {
    district_id: number;
    selected_crop: string;
    land_area_ha: number;
    budget_inr: number;
    confirmed_soil_type: string;
    rainfall_override_mm: number;
    planting_season: string;
    planned_start_date: string;
  }) {
    return this.request<any>("/api/v1/simulation/run", {
      method: "POST",
      body: JSON.stringify(params),
    });
  }

  static async lookupDistrict(lat: number, lon: number) {
    return this.request<any>(
      `/api/v1/spatial/lookup?lat=${lat}&lon=${lon}`,
      { method: "GET" }
    );
  }

  static async getDistricts(state?: string) {
    const query = state ? `?state=${encodeURIComponent(state)}` : "";
    return this.request<any[]>(`/api/v1/map/districts${query}`, { method: "GET" });
  }
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  retries = 2,
  delay = 1000
): Promise<{ data: T; error?: undefined } | { data?: undefined; error: ApiError }> {
  for (let i = 0; i <= retries; i++) {
    try {
      const data = await fn();
      return { data };
    } catch (err) {
      const error = err as ApiError;
      if (!error.retryable || i === retries) {
        return { error };
      }
      await new Promise((r) => setTimeout(r, delay * (i + 1)));
    }
  }
  return { error: new Error("Max retries exceeded") as ApiError };
}
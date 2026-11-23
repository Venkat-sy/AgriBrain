export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "https://agribrain-backend.onrender.com";

export interface ApiError extends Error {
  status?: number;
  retryable?: boolean;
}

interface ChatFarmContext {
  is_context_aware?: boolean;
  coordinates?: { lat: number; lon: number };
  soilParams?: { ph: number; texture: string; organic_carbon: number; n: number; p: number; k: number };
  annualRainfall?: number;
  selectedCrop?: string | null;
  farmParams?: Record<string, unknown> | null;
  simulationResults?: Record<string, unknown> | null;
  calendarStages?: unknown[] | null;
  image?: string;
  endpoint?: string;
}

interface CropRecommendationItem {
  crop_name: string;
  confidence_score?: number;
  expected_yield_tons_per_ha?: number;
  [key: string]: unknown;
}

interface SimulationApiResult {
  district?: string | null;
  agro_zone?: string | null;
  area_acres?: number;
  setup_type?: 'seasonal' | 'perennial';
  weather?: Record<string, unknown> | null;
  soil?: Record<string, unknown> | null;
  rainfall_forecast?: unknown[];
  ranked_crops?: unknown[];
  recommended_crop?: string | null;
  timeline?: unknown[];
  alternatives?: unknown[];
  [key: string]: unknown;
}

interface DistrictLookupResult {
  district_id?: number;
  district?: string;
  soil_type?: string;
  agro_zone?: string;
  weather?: { temp?: number; rainfall?: number; humidity?: number };
  soil?: { pH?: number; N?: number; P?: number; K?: number };
  [key: string]: unknown;
}

interface WeatherApiResult {
  weather: { temp?: number; humidity?: number; rainfall?: number };
  [key: string]: unknown;
}

interface DistrictItem {
  id: number;
  name: string;
  state: string;
  [key: string]: unknown;
}

// Adjusted API structure for sending correctly; payload includes prompt, coordinates.
let sessionId: string | null = null;

function getSessionId(): string {
  if (!sessionId) {
    sessionId = crypto.randomUUID();
  }
  return sessionId;
}

export function resetSessionId(): void {
  sessionId = null;
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
      context?: ChatFarmContext
    ) {
      const hasImage = context?.image != null && context.image.startsWith("data:image/");
      const endpoint = context?.endpoint || (hasImage ? "/api/v1/chat/troubleshoot-vision" : "/api/v1/chat/troubleshoot");
   
      const currentSessionId = getSessionId();

      let body: BodyInit;
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      if (hasImage) {
        // For vision endpoint, send multipart/form-data
        body = new FormData();
        body.append("session_id", currentSessionId);
        body.append("user_question", message || "Analyze this image");
        body.append("context", JSON.stringify({
          coordinates: context?.coordinates,
          soilParams: context?.soilParams,
          annualRainfall: context?.annualRainfall,
          selectedCrop: context?.selectedCrop,
          farmParams: context?.farmParams,
          simulationResults: context?.simulationResults,
          calendarStages: context?.calendarStages,
        }));
     
        // Convert base64 to blob
        const base64Data = context.image!.split(",")[1];
        const mimeType = context.image!.split(",")[0].split(":")[1].split(";")[0];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: mimeType });
        body.append("image", blob, "image.jpg");
     
        // Don't set Content-Type for FormData - browser will set it with boundary
        delete headers["Content-Type"];
      } else {
              body = JSON.stringify({
                session_id: currentSessionId,
                message: message,
                context: context?.is_context_aware ? {
                  coordinates: context.coordinates,
                  soilParams: context.soilParams,
                  annualRainfall: context.annualRainfall,
                  selectedCrop: context.selectedCrop,
                  farmParams: context.farmParams,
                  simulationResults: context.simulationResults,
                  calendarStages: context.calendarStages,
                } : undefined,
              });
            }

      return this.request<{ response: string; session_id: string }>(endpoint, {
        method: "POST",
        headers,
        body,
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
    return this.request<{ recommendations: CropRecommendationItem[] }>("/api/v1/crop/recommend", {
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
    return this.request<SimulationApiResult>("/api/v1/simulation/run", {
      method: "POST",
      body: JSON.stringify(params),
    });
  }

  static async lookupDistrict(lat: number, lon: number) {
      return this.request<DistrictLookupResult>(
        `/api/v1/spatial/lookup?lat=${lat}&lon=${lon}`,
        { method: "GET" }
      );
    }

    static async getWeather(lat: number, lon: number) {
      return this.request<WeatherApiResult>(
        `/api/v1/spatial/weather?lat=${lat}&lon=${lon}`,
        { method: "GET" }
      );
    }

    static async getDistricts(state?: string) {
    const query = state ? `?state=${encodeURIComponent(state)}` : "";
    return this.request<DistrictItem[]>(`/api/v1/map/districts${query}`, { method: "GET" });
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
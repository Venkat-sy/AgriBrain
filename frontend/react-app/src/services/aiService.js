// The chat endpoint is configurable via an environment variable.
// In development Vite serves a local middleware at /api/chat.
// For production the frontend is hosted on GitHub Pages and must call the
// backend directly. The VITE_BACKEND_URL variable is supplied at build time.
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || '';
const CHAT_ENDPOINT = `${BACKEND_URL}/api/chat`;

export function buildFarmContext({
    farms = [],
    fields = [],
    crops = [],
    weather = null,
    alerts = [],
    recommendations = [],
} = {}) {
    const cropById = Object.fromEntries(crops.map((crop) => [crop.id, crop]));
    const farmById = Object.fromEntries(farms.map((farm) => [farm.id, farm]));

    return {
        generatedAt: new Date().toISOString(),
        farms: farms.map((farm) => ({
            id: farm.id,
            name: farm.name,
            location: farm.location,
            areaHa: farm.area,
            status: farm.status,
            soilType: farm.soilType,
        })),
        fields: fields.map((field) => {
            const farm = farmById[field.farmId];
            const crop = cropById[field.cropId];
            return {
                id: field.id,
                name: field.name,
                farmName: farm?.name,
                areaHa: field.area,
                status: field.status,
                soilHealth: field.soilHealth,
                crop: crop ? `${crop.name} (${crop.variety})` : null,
                growthStage: crop?.growthStage,
                cropHealth: crop?.healthStatus,
                plantingDate: field.plantingDate,
                expectedHarvest: field.expectedHarvest,
            };
        }),
        crops: crops.map((crop) => ({
            id: crop.id,
            name: crop.name,
            variety: crop.variety,
            growthStage: crop.growthStage,
            healthStatus: crop.healthStatus,
            daysPlanted: crop.daysPlanted,
            expectedYield: crop.expectedYield,
            currentConditions: crop.currentConditions || null,
        })),
        weather,
        alerts: alerts.map((alert) => ({
            type: alert.type,
            title: alert.title,
            message: alert.message,
            farmName: farmById[alert.farmId]?.name,
            fieldName: fields.find((field) => field.id === alert.fieldId)?.name,
            actionRequired: alert.actionRequired,
            read: alert.read,
        })),
        recommendations: recommendations.map((rec) => ({
            crop: rec.crop,
            recommendation: rec.recommendation,
            reasoning: rec.reasoning,
            priority: rec.priority,
            action: rec.action,
            confidence: rec.confidence,
        })),
    };
}

export async function sendChatMessage({ messages, farmContext, userMessage }) {
    // Send request to the backend (or Vercel serverless function) handling AI chat.
    const response = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages, farmContext, userMessage }),
    });

    const data = await response.json().catch(() => ({}));
    // Preserve original error handling but adapt to the backend response shape.
    if (!response.ok) {
        const error = new Error(data.error || 'Failed to get a response from AgriBrain AI');
        error.code = data.code || 'REQUEST_FAILED';
        error.hint = data.hint;
        throw error;
    }

    // The backend now returns { message, provider, model }. Fall back to older field names for compatibility.
    const content = data.message ?? data.text ?? '';
    const provider = data.provider ?? 'unknown';
    const model = data.model ?? 'unknown';

    return { content, provider, model };
}

export default {
    sendChatMessage,
    buildFarmContext,
};

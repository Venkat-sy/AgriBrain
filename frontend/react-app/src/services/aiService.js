const CHAT_ENDPOINT = '/api/chat';

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
    const response = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages, farmContext, userMessage }),
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        const error = new Error(data.error || 'Failed to get a response from AgriBrain AI');
        error.code = data.code || 'REQUEST_FAILED';
        error.hint = data.hint;
        throw error;
    }

    return {
        content: data.message,
        provider: data.provider,
        model: data.model,
    };
}

export default {
    sendChatMessage,
    buildFarmContext,
};

// Vite's dev middleware runs in Node where the global fetch API is available (Node >=18).

/**
 * Handles POST /api/chat requests.
 * Expected payload (as sent by frontend aiService):
 * {
 *   messages: [{role: 'user'|'assistant', content: string}],
 *   farmContext: Object,
 *   userMessage: string
 * }
 *
 * The handler now directly calls a local model implementation via FastAPI
 * endpoints (e.g., crop recommendation). If the request cannot be handled by a
 * local model, a deterministic mock fallback is used. No external LLM APIs are
 * referenced and the GEMINI_API_KEY environment variable is ignored.
 */

/** Helper that decides which local model to invoke based on the user query.
 *  Currently only the crop‑recommendation model is wired. It can be extended to
 *  call other FastAPI endpoints (rainfall, soil, yield, simulation, etc.).
 */
async function runMyModel({ userMessage, farmContext }) {
    const lower = (userMessage || '').toLowerCase();

    // Simple intent detection – if the user asks about crops or recommendations
    const wantsCrop = lower.includes('crop') || lower.includes('recommend') || lower.includes('what should i grow');

    if (wantsCrop) {
        // Build a request payload compatible with CropRecommendationRequest schema.
        const firstFarm = (farmContext?.farms?.[0]) || {};
        const payload = {
            district_id: 1, // default – in a real deployment this would be derived from the user's location
            soil_type: firstFarm.soilType || 'unknown',
            rainfall_mm: farmContext?.weather?.current?.rainfall_mm ?? 0,
            temperature_c: farmContext?.weather?.current?.temperature ?? null,
            humidity_percent: farmContext?.weather?.current?.humidity ?? null,
            ph: firstFarm?.ph ?? null,
            n: firstFarm?.n ?? null,
            p: firstFarm?.p ?? null,
            k: firstFarm?.k ?? null,
            top_k: 5,
        };

        try {
            const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
            const res = await fetch(`${backendUrl}/api/v1/crop/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!res.ok) return null;
            const data = await res.json();
            if (data?.recommendations?.length) {
                const recs = data.recommendations
                    .map(r => `${r.crop_name} (${(r.confidence * 100).toFixed(1)}%)`)
                    .join(', ');
                return {
                    message: `Recommended crops based on your context: ${recs}`,
                    provider: 'local-model',
                    model: data.model_version || 'crop-recommendation',
                };
            }
        } catch (e) {
            console.error('Local model invocation failed', e);
            return null;
        }
    }

    // Add more intent branches here (e.g., rainfall, soil, yield) as needed.
    return null; // indicate no suitable local model was used
}

export const handleChatRequest = async (req, res) => {
    if (req.method !== 'POST') {
        res.statusCode = 405;
        res.end('Method not allowed');
        return;
    }

    // Collect request body
    let body = '';
    req.on('data', chunk => {
        body += chunk.toString();
    });

    req.on('end', async () => {
        try {
            const { messages, farmContext, userMessage } = JSON.parse(body);

            // 1️⃣ Try local model inference
            const modelReply = await runMyModel({ userMessage, farmContext });
            if (modelReply) {
                res.setHeader('Content-Type', 'application/json');
                res.statusCode = 200;
                res.end(
                    JSON.stringify({
                        message: modelReply.message,
                        provider: modelReply.provider,
                        model: modelReply.model,
                        timestamp: new Date().toISOString(),
                    })
                );
                return;
            }

            // 2️⃣ Mock fallback – deterministic rule‑based response.
            const lower = (userMessage || '').toLowerCase();
            const ctx = farmContext || {};
            // Simulate latency for a smoother UI experience.
            await new Promise(r => setTimeout(r, 1500));

            let reply = '';
            if (lower.includes('water') || lower.includes('irrigate') || lower.includes('moisture')) {
                const alert = ctx.alerts?.find(a => a.message?.toLowerCase().includes('moisture') || a.message?.toLowerCase().includes('water'));
                if (alert) {
                    reply = `I recommend checking **Field ${alert.fieldId}**. Recent alert:\n> ${alert.message}\nCurrent weather: ${ctx.weather?.current?.condition}, ${ctx.weather?.current?.temperature}°C.`;
                } else {
                    reply = `Soil moisture appears stable. Weather today: ${ctx.weather?.current?.condition}, ${ctx.weather?.current?.temperature}°C.`;
                }
            } else if (lower.includes('yield') || lower.includes('harvest')) {
                const harvestAlert = ctx.alerts?.find(a => a.message?.toLowerCase().includes('harvest'));
                reply = harvestAlert ? `Good news: ${harvestAlert.title}\n${harvestAlert.message}` : 'Your crops look good. Check AI Insights for detailed forecasts.';
            } else if (lower.includes('yellow') || lower.includes('disease') || lower.includes('sick')) {
                const healthAlert = ctx.alerts?.find(a => a.type === 'critical' || a.type === 'warning');
                if (healthAlert && healthAlert.message?.toLowerCase().includes('nutrient')) {
                    reply = `Yellowing may indicate a nutrient issue. Alert: ${healthAlert.title} – ${healthAlert.message}. Recommended: soil test and appropriate fertilization.`;
                } else {
                    reply = 'Yellowing can have many causes. No critical alerts are present at the moment.';
                }
            } else if (lower.includes('weather') || lower.includes('rain')) {
                reply = `Current weather: ${ctx.weather?.current?.condition} at ${ctx.weather?.current?.temperature}°C.`;
            } else {
                reply = `I understand you asked: "${userMessage}". I’m here to help with farm‑related queries.`;
            }

            res.setHeader('Content-Type', 'application/json');
            res.statusCode = 200;
            res.end(
                JSON.stringify({
                    message: reply,
                    provider: 'mock',
                    model: 'local-mock',
                    timestamp: new Date().toISOString(),
                })
            );
        } catch (err) {
            console.error('Chat API Error:', err);
            res.statusCode = 500;
            res.end(JSON.stringify({ error: 'Failed to process chat request.', code: 'SERVER_ERROR' }));
        }
    });
};

import { IncomingMessage, ServerResponse } from 'http';

/**
 * Very basic mock handler for local development if no API keys are provided.
 * In a real backend, this would use the Gemini or OpenAI SDK.
 */
export const handleChatRequest = async (req, res) => {
    // Only accept POST
    if (req.method !== 'POST') {
        res.statusCode = 405;
        res.end('Method not allowed');
        return;
    }

    // Read body
    let body = '';
    req.on('data', chunk => {
        body += chunk.toString();
    });

    req.on('end', async () => {
        try {
            const data = JSON.parse(body);
            const { message, context } = data;

            // Optional: You could read process.env.GEMINI_API_KEY here and call Gemini REST API directly.
            // For this project, we'll implement a smart local mock that reads the context.

            let aiResponse = "";
            const lowerMsg = message.toLowerCase();

            // Simulate network delay
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Basic context-aware logic
            if (lowerMsg.includes('water') || lowerMsg.includes('irrigate') || lowerMsg.includes('moisture')) {
                const alert = context?.alerts?.find(a => a.message.toLowerCase().includes('moisture') || a.message.toLowerCase().includes('water'));
                if (alert) {
                    aiResponse = `I recommend checking **Field ${alert.fieldId}**. Based on recent alerts:\n\n> "${alert.message}"\n\nGiven the current weather (${context?.weather?.current?.condition}, ${context?.weather?.current?.temperature}°C), irrigation is recommended.`;
                } else {
                    aiResponse = `Based on your current telemetry, soil moisture levels across your active fields appear stable. The weather today is **${context?.weather?.current?.condition}** with a temperature of **${context?.weather?.current?.temperature}°C**.\n\n*If you are concerned about a specific field, please provide the field name.*`;
                }
            } else if (lowerMsg.includes('yield') || lowerMsg.includes('harvest')) {
                const harvestAlert = context?.alerts?.find(a => a.message.toLowerCase().includes('harvest'));
                if (harvestAlert) {
                    aiResponse = `Good news regarding your harvest! \n\n**${harvestAlert.title}**\n${harvestAlert.message}\n\nPrepare your equipment and storage facilities accordingly.`;
                } else {
                    aiResponse = `Your crops are progressing well. For detailed yield predictions, please check the **AI Insights** tab which uses satellite imagery and historical data to forecast your harvest.`;
                }
            } else if (lowerMsg.includes('yellow') || lowerMsg.includes('disease') || lowerMsg.includes('sick')) {
                const healthAlert = context?.alerts?.find(a => a.type === 'critical' || a.type === 'warning');
                if (healthAlert && healthAlert.message.toLowerCase().includes('nutrient')) {
                    aiResponse = `Yellowing leaves often indicate a nutrient deficiency or pest issue. \n\nI noticed an alert for your farm:\n**${healthAlert.title}** - ${healthAlert.message}\n\n### Recommended Actions:\n1. Conduct a localized soil test.\n2. Apply the recommended fertilization mix.\n3. Monitor the affected area over the next 7 days.`;
                } else {
                    aiResponse = `Yellowing crops (chlorosis) can be caused by several factors:\n\n*   **Nitrogen Deficiency:** Older leaves turn yellow first.\n*   **Water Stress:** Overwatering or underwatering.\n*   **Diseases:** Fungal infections or viruses.\n\nI don't see any critical health alerts in your telemetry right now. Please monitor the field and consider uploading a drone image to the Analytics module for detailed leaf-level analysis.`;
                }
            } else if (lowerMsg.includes('weather') || lowerMsg.includes('rain')) {
                 aiResponse = `The current weather is **${context?.weather?.current?.condition}** at ${context?.weather?.current?.temperature}°C. \n\nLooking at the forecast:\n* Tomorrow: ${context?.weather?.forecast?.[1]?.condition} (${context?.weather?.forecast?.[1]?.temp}°C)\n* Day after: ${context?.weather?.forecast?.[2]?.condition} (${context?.weather?.forecast?.[2]?.temp}°C)\n\nPlan your field operations accordingly.`;
            } else {
                aiResponse = `I understand you're asking about: "${message}". \n\nAs your AgriBrain assistant, I'm currently monitoring **${context?.farms?.length || 0} farms** and **${context?.fields?.length || 0} fields**. \n\nIs there a specific field or crop you'd like me to analyze?`;
            }

            res.setHeader('Content-Type', 'application/json');
            res.statusCode = 200;
            res.end(JSON.stringify({ 
                text: aiResponse,
                timestamp: new Date().toISOString()
            }));

        } catch (error) {
            console.error('Chat API Error:', error);
            res.statusCode = 500;
            res.end(JSON.stringify({ error: 'Failed to process chat request.' }));
        }
    });
};

import React, { useState, useEffect, useRef } from 'react';
import { useApp } from '../../context/AppContext';
import { sendChatMessage, buildFarmContext } from '../../services/aiService';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import SuggestedQuestions from './SuggestedQuestions';
import TypingIndicator from './TypingIndicator';
import { Sparkles, Trash2, AlertCircle, RefreshCw, Info } from 'lucide-react';
import './AIChat.css';

const INITIAL_WELCOME = {
    id: 'welcome-1',
    role: 'assistant',
    content: `👋 Hey there! I’m **AgriBrain AI**, your personal farm‑side companion. 🌱

🔎 I’m plugged into **live** data from all your farms, fields, soils, crops, weather stations and alerts – so I can give you **actionable** advice, not just generic facts.

💬 **Ask me anything**:
* **Field‑by‑field check‑ups** – e.g. *"What’s the status of Field A‑1?"* or *"Should I water today?"*
* **Disease & pest detective** – e.g. *"Why are my leaves turning yellow?"*
* **Soil & nutrition tips** – e.g. *"How can I boost soil health?"*
* **Yield & harvest forecasts** – e.g. *"When is my wheat ready for harvest?"*

✨ **Try one of the quick prompts below** or type your own question to dive in!`,
    timestamp: new Date(),
};

const AIChat = () => {
    const appContext = useApp();
    const [messages, setMessages] = useState(() => {
        const saved = localStorage.getItem('agribrain_chat_history');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (Array.isArray(parsed) && parsed.length > 0) return parsed;
            } catch {
                // Ignore invalid cache
            }
        }
        return [INITIAL_WELCOME];
    });

    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        try {
            localStorage.setItem('agribrain_chat_history', JSON.stringify(messages));
        } catch {
            // Ignore storage errors
        }
    }, [messages]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading, error]);

    const handleSend = async (customMessage) => {
        const textToSend = customMessage || input;
        if (!textToSend.trim() || loading) return;

        setError(null);
        const userMsg = {
            id: `msg-${Date.now()}`,
            role: 'user',
            content: textToSend.trim(),
            timestamp: new Date(),
        };

        const updatedHistory = [...messages, userMsg];
        setMessages(updatedHistory);
        setInput('');
        setLoading(true);

        try {
            const farmContext = buildFarmContext(appContext);
            const apiMessages = updatedHistory.map((m) => ({
                role: m.role,
                content: m.content,
            }));

            const response = await sendChatMessage({
                messages: apiMessages,
                farmContext,
                userMessage: userMsg.content,
            });

            const aiMsg = {
                id: `msg-${Date.now() + 1}`,
                role: 'assistant',
                content: response.content,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, aiMsg]);
        } catch (err) {
            setError({
                message: err.message || 'Unable to fetch AI response.',
                code: err.code,
                hint: err.hint,
            });
        } finally {
            setLoading(false);
        }
    };

    const handleClearChat = () => {
        if (window.confirm('Are you sure you want to clear this conversation?')) {
            setMessages([INITIAL_WELCOME]);
            setError(null);
            localStorage.removeItem('agribrain_chat_history');
        }
    };

    const handleRetry = () => {
        const lastUserMessage = [...messages].reverse().find((m) => m.role === 'user');
        if (lastUserMessage) {
            handleSend(lastUserMessage.content);
        }
    };

    const userMessageCount = messages.filter((m) => m.role === 'user').length;


    return (
        <div className="page-container fade-in chat-page-container">
            <div className="chat-header-card">
                <div className="chat-header-info">
                    <div className="chat-header-icon">
                        <Sparkles size={24} />
                    </div>
                    <div>
                        <h1 className="chat-header-title">AgriBrain AI Assistant</h1>
                        <p className="chat-header-subtitle">
                            Ask anything about your farm, crops, soil, weather, diseases, irrigation, or farming decisions.
                        </p>
                    </div>
                </div>

                <div className="chat-header-actions">
                    <div className="chat-status-badge">
                        <span className="pulse-dot green" /> Context Aware
                    </div>
                    {messages.length > 1 && (
                        <button
                            type="button"
                            className="chat-clear-btn"
                            onClick={handleClearChat}
                            title="Clear conversation"
                        >
                            <Trash2 size={16} /> Clear Chat
                        </button>
                    )}
                </div>
            </div>

            <div className="chat-window-card">
                <div className="chat-messages-scroll">
                    {messages.map((msg) => (
                        <ChatMessage key={msg.id} message={msg} />
                    ))}

                    {loading && <TypingIndicator />}

                    {error && (
                        <div className="chat-error-banner" role="alert">
                            <div className="chat-error-icon">
                                <AlertCircle size={20} />
                            </div>
                            <div className="chat-error-content">
                                <div className="chat-error-title">AI Assistant Notice</div>
                                <p className="chat-error-text">{error.message}</p>
                                {error.hint && <p className="chat-error-hint">{error.hint}</p>}
                                <div className="chat-error-actions">
                                    <button
                                        type="button"
                                        className="chat-retry-btn"
                                        onClick={handleRetry}
                                    >
                                        <RefreshCw size={14} /> Try Again
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {userMessageCount < 2 && (
                    <div className="chat-prompts-section">
                        <div className="chat-prompts-label">
                            <Info size={14} /> Suggested prompts:
                        </div>
                        <SuggestedQuestions
                            onSelect={(question) => handleSend(question)}
                            disabled={loading}
                        />
                    </div>
                )}

                <div className="chat-input-wrapper">
                    <ChatInput
                        value={input}
                        onChange={setInput}
                        onSend={() => handleSend()}
                        disabled={loading}
                    />
                    <div className="chat-disclaimer">
    ⚠️ AI suggestions are **data‑driven** but not a substitute for on‑ground checks. Verify critical actions with your agronomist or field crew before acting.
</div>
                </div>
            </div>
        </div>
    );
};

export default AIChat;


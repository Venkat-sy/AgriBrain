"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Bot, User, Loader2, Sprout, AlertCircle, RefreshCw, WifiOff } from "lucide-react";
import { useFarm } from "@/context/FarmContext";
import { ApiService, withRetry } from "@/services/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatAssistantProps {
  is_context_aware?: boolean;
}

export default function ChatAssistant({ is_context_aware = false }: ChatAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const {
    selectedCrop,
    farmParams,
    simulationResults,
    calendarStages,
    coordinates,
    soilParams,
    annualRainfall,
  } = useFarm();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;

    const userMessage = messageText;
    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage, timestamp: new Date() },
    ]);
    setInput("");
    setIsLoading(true);
    setConnectionError(null);

    const contextPayload = is_context_aware
      ? {
          selectedCrop,
          farmParams,
          simulationResults,
          calendarStages: calendarStages?.slice(0, 3),
          coordinates: coordinates ? { lat: coordinates.lat, lon: coordinates.lon } : undefined,
          soilParams: soilParams
            ? {
                ph: soilParams.ph,
                texture: soilParams.texture,
                organic_carbon: soilParams.organic_carbon,
                n: soilParams.n,
                p: soilParams.p,
                k: soilParams.k,
              }
            : undefined,
          annualRainfall: annualRainfall ?? undefined,
        }
      : undefined;

    const result = await withRetry(
      () =>
        ApiService.sendChatMessage(userMessage, {
          is_context_aware,
          ...contextPayload,
        }),
      2,
      1000
    );

    if (result.error) {
      const error = result.error;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            error.retryable
              ? "⚠️ I'm having trouble connecting to the server right now. Please try again in a moment."
              : `⚠️ Error: ${error.message}`,
          timestamp: new Date(),
        },
      ]);
      setConnectionError(error.message);
    } else if (result.data?.response) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.data.response,
          timestamp: new Date(),
        },
      ]);
    }

    setIsLoading(false);
    inputRef.current?.focus();
  };

  const retryLastMessage = () => {
    if (messages.length > 0) {
      const lastUserMessage = [...messages].reverse().find((m) => m.role === "user");
      if (lastUserMessage) {
        sendMessage(lastUserMessage.content);
      }
    }
  };

  const formatTime = (d: Date) =>
    d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });

  const glassCard = "bg-white/5 dark:bg-slate-900/5 backdrop-blur-md border border-white/10 dark:border-slate-800/50 rounded-2xl shadow-xl shadow-slate-900/5";
  const inputClass = "w-full px-4 py-3 bg-white/5 dark:bg-slate-800/30 border border-white/10 dark:border-slate-700/50 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed";

  return (
    <div className={`flex flex-col h-full ${glassCard} overflow-hidden`}>
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-white/10 dark:border-slate-700/50">
        <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
          <Sprout className="w-5 h-5 text-green-500" />
        </div>
        <div className="flex-1">
          <h2 className="font-bold text-lg text-slate-900 dark:text-white">
            {is_context_aware ? "Expert Agronomist" : "AgriBrain Assistant"}
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {is_context_aware
              ? "AI-powered expert with full farm context"
              : "AI-powered farming advisor • Always online"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {connectionError && (
            <button
              onClick={retryLastMessage}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-full hover:bg-amber-100 dark:hover:bg-amber-900/40 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              Retry
            </button>
          )}
          <div
            className={`w-2 h-2 rounded-full ${
              connectionError ? "bg-red-500" : "bg-green-500"
            }`}
          />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className="flex gap-3">
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                msg.role === "user"
                  ? "bg-blue-500/20"
                  : "bg-green-500/20"
              }`}
            >
              {msg.role === "user" ? (
                <User className="w-4 h-4 text-blue-500" />
              ) : (
                <Bot className="w-4 h-4 text-green-500" />
              )}
            </div>
            <div className="flex-1">
              <div
                className={`px-4 py-3 rounded-2xl ${
                  msg.role === "user"
                    ? "bg-blue-500/10 text-slate-900 dark:text-blue-100 rounded-br-sm"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-sm"
                }`}
              >
              {msg.role === "assistant" ? (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                msg.content
              )}
              </div>
              <span className="text-[10px] text-slate-400 px-1">{formatTime(msg.timestamp)}</span>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex gap-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center">
              <Bot className="w-4 h-4 text-green-500" />
            </div>
            <div className="bg-slate-100 dark:bg-slate-800 rounded-2xl rounded-bl-sm px-4 py-3">
              <div className="flex gap-1 items-center h-4">
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested questions (shown when empty) */}
      {messages.length === 0 && (
        <div className="px-4 pb-2 border-t border-white/10 dark:border-slate-700/50">
          <div className="text-center text-slate-500 dark:text-slate-400 py-4 mb-2">
            <p className="text-sm">
              {is_context_aware
                ? "Chat with your expert agronomist — I have full context of your farm simulation."
                : "Ask me anything about crop recommendations, soil health, or farming practices!"}
            </p>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">
            Suggested questions:
          </p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                className="text-xs px-3 py-1.5 bg-green-500/10 dark:bg-green-900/20 text-green-600 dark:text-green-400 border border-green-200 dark:border-green-800 rounded-full hover:bg-green-100 dark:hover:bg-green-900/40 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Connection error banner */}
      {connectionError && !isLoading && (
        <div className="px-4 py-3 border-t border-white/10 dark:border-slate-700/50 bg-red-500/5 dark:bg-red-900/10">
          <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
            <WifiOff className="w-4 h-4" />
            <span>Connection issue: {connectionError}</span>
            <button
              onClick={retryLastMessage}
              className="ml-auto px-3 py-1 text-xs font-medium text-red-600 dark:text-red-400 bg-red-500/10 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-full hover:bg-red-500/20 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="px-4 py-3 border-t border-white/10 dark:border-slate-700/50 bg-slate-50/50 dark:bg-slate-800/50">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            placeholder="Ask about crops, soil, rainfall, fertilizers..."
            className={inputClass}
            disabled={isLoading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || isLoading}
            className="px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-1.5 shadow-lg shadow-green-500/25"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

const SUGGESTED_QUESTIONS = [
  "What crops grow best in black soil?",
  "When should I sow wheat in Punjab?",
  "How much water does rice need per season?",
  "What fertilizer is best for cotton?",
  "How do I improve soil pH for vegetables?",
  "What are signs of nitrogen deficiency?",
];
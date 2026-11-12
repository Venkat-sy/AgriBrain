 "use client";

 import { useState } from "react";
 import { Send } from "lucide-react";
 import { useFarm } from "@/context/FarmContext";

 interface Message {
   role: "user" | "assistant";
   content: string;
 }

 interface ChatAssistantProps {
   is_context_aware?: boolean;
 }

 export default function ChatAssistant({ is_context_aware = false }: ChatAssistantProps) {
   const [messages, setMessages] = useState<Message[]>([]);
   const [input, setInput] = useState("");
   const [isLoading, setIsLoading] = useState(false);
   const { simulationResults, selectedCrop, farmParams, calendarStages } = useFarm();

   const sendMessage = async () => {
     if (!input.trim() || isLoading) return;

     const userMessage = input;
     setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
     setInput("");
     setIsLoading(true);

     try {
       const response = await fetch("/api/chat", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ 
           message: userMessage,
           is_context_aware: is_context_aware,
           context: is_context_aware ? {
             selectedCrop,
             farmParams,
             simulationResults,
             calendarStages: calendarStages?.slice(0, 3)
           } : undefined
         }),
       });

       const data = await response.json();
       setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
     } catch (error) {
       setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error." }]);
     } finally {
       setIsLoading(false);
     }
   };

   return (
     <div className="bg-white rounded-lg shadow-md border border-gray-200 flex flex-col h-[500px]">
       <div className="p-4 border-b border-gray-200">
         <div className="flex items-center justify-between">
           <h3 className="font-semibold text-gray-900">AI Assistant</h3>
           {is_context_aware && (
             <span className="px-2 py-1 text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300 rounded-full">
               Context Aware
             </span>
           )}
         </div>
       </div>
       <div className="flex-1 overflow-y-auto p-4 space-y-4">
         {messages.length === 0 && (
           <div className="text-center text-gray-500 py-8">
             <p>{is_context_aware ? "Chat with your expert agronomist - I have full context of your farm simulation." : "Ask me anything about crop recommendations, soil health, or farming practices!"}</p>
           </div>
         )}
         {messages.map((msg, idx) => (
           <div
             key={idx}
             className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
           >
             <div
               className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                 msg.role === "user"
                   ? "bg-green-600 text-white rounded-br-none"
                   : "bg-gray-100 text-gray-900 rounded-bl-none"
               }`}
             >
               {msg.content}
             </div>
           </div>
         ))}
         {isLoading && (
           <div className="flex justify-start">
             <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-2xl rounded-bl-none animate-pulse">
               <span className="flex space-x-1">
                 <span>.</span>
                 <span>.</span>
                 <span>.</span>
               </span>
             </div>
           </div>
         )}
       </div>
       <div className="p-4 border-t border-gray-200">
         <div className="flex gap-2">
           <input
             type="text"
             value={input}
             onChange={(e) => setInput(e.target.value)}
             onKeyPress={(e) => e.key === "Enter" && sendMessage()}
             placeholder="Type your question..."
             className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
             disabled={isLoading}
           />
           <button
             onClick={sendMessage}
             disabled={!input.trim() || isLoading}
             className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
           >
             <Send className="w-5 h-5" />
           </button>
         </div>
       </div>
     </div>
   );
 }
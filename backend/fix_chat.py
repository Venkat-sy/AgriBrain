with open('api/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the generate_advice function
start = content.find('def generate_advice')
end = content.find('def generate_rule_based_advice')
old_func = content[start:end]

new_func = '''def generate_advice(question: str, chat_history: list, is_context_aware: bool = False) -> str:
    """Generate farming advice based on the question and optional chat context.

    First tries to use Gemini API for intelligent responses.
    Falls back to rule-based advice generation if API is unavailable.
    """
    # Try to import and use Gemini
    try:
        from google import genai
        from backend.core.config import settings

        if settings.GOOGLE_API_KEY:
            client = genai.Client(api_key=settings.GOOGLE_API_KEY)

            # Build context from chat history
            context = ""
            if is_context_aware and chat_history:
                for msg in chat_history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if role == "system":
                        context += f"Farm Context: {content}\\n"
                    elif role == "user":
                        context += f"Farmer: {content}\\n"
                    elif role == "assistant":
                        context += f"Advisor: {content}\\n"

            system_prompt = """You are an expert agricultural advisor for Indian farmers. Speak naturally and conversationally - like a knowledgeable farmer talking to another farmer.

Provide specific, practical advice suitable for Indian farming conditions.
- Be direct and conversational, not formal or academic
- Use natural language, not bullet-point dumps
- Include relevant details like timing, quantities, and local practices
- Keep responses concise but helpful
- If you don't know something exactly, say so and suggest what to check
- NO markdown headers (##), NO bullet lists (•), NO bold/italic formatting
- Just plain, helpful conversation"""

            # Use the new chat API
            chat = client.chats.create(
                model="gemini-1.5-flash",
                config={"system_instruction": system_prompt}
            )
            
            full_prompt = f"""Context:
{context}

Question: {question}"""
            
            response = chat.send_message(full_prompt)
            if response.text:
                return response.text.strip()
    except Exception as e:
        # Log error and fall back to rule-based advice
        print(f"Gemini API error: {e}")
        pass

    # Fallback: Rule-based advice generation
    return generate_rule_based_advice(question, chat_history, is_context_aware)

'''

new_content = content[:start] + new_func + content[end:]

with open('api/chat.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Done')
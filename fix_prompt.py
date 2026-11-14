with open('backend/api/chat.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Find the start of the prompt
start = c.find('prompt = f"""You are an expert agricultural advisor')
if start == -1:
    print('Could not find prompt')
    exit(1)

# Find the end of the prompt (the closing """)
end = c.find('"""', start + 15)
if end == -1:
    print('Could not find end of prompt')
    exit(1)
end += 3  # Include the closing """

# Get the exact old prompt
old_prompt = c[start:end]
print(f'Found prompt length: {len(old_prompt)}')
print(repr(old_prompt[:200]))

# Create new prompt
new_prompt = '''prompt = f"""You are an expert agricultural advisor for Indian farmers. Speak naturally and conversationally - like a knowledgeable farmer talking to another farmer.

Context:
{context}

Question: {question}

Provide specific, practical advice suitable for Indian farming conditions. 
- Be direct and conversational, not formal or academic
- Use natural language, not bullet-point dumps
- Include relevant details like timing, quantities, and local practices
- Keep responses concise but helpful
- If you don't know something exactly, say so and suggest what to check
- NO markdown headers (##), NO bullet lists (•), NO bold/italic formatting
- Just plain, helpful conversation\"""'''

# Replace
c = c[:start] + new_prompt + c[end:]

with open('backend/api/chat.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('SUCCESS: Replaced prompt')
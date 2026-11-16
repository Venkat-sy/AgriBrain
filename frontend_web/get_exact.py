with open(r'C:/Users/USER/Downloads/FinalYearProject/frontend_web/src/app/simulate/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the problematic area - the first occurrence
idx = text.find('</>)')
print('Found at idx:', idx)

# Get a larger context - going further back to see the full ternary
context = text[idx-1000:idx+500]
print('=== CONTEXT ===')
print(context)

# Also write to file for inspection
with open('context.txt', 'w', encoding='utf-8') as f2:
    f2.write(context)
print('Written to context.txt')
import pathlib

c = pathlib.Path('frontend_web/src/components/HomeChatbot.tsx').read_text(encoding='utf-8')
print('Length:', len(c))

# Find inputClass
idx = c.find('inputClass')
if idx == -1:
    idx = c.find('const inputClass')
print(c[idx:idx+500])
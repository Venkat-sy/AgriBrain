import pathlib

c = pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').read_text(encoding='utf-8')
print('Length:', len(c))

# Find return statement
idx = c.find('return (')
print(c[idx+9000:idx+12000])
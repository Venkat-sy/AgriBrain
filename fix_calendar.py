import pathlib

c = pathlib.Path('frontend_web/src/app/calendar/page.tsx').read_text(encoding='utf-8')
print('Length:', len(c))

# Find second return statement
idx1 = c.find('return (')
idx2 = c.find('return (', idx1 + 10)
print(f'Second return at: {idx2}')
print(c[idx2+8000:idx2+12000])
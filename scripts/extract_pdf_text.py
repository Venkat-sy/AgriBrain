from pathlib import Path
import fitz

root = Path(r'C:\Users\USER\OneDrive\Desktop\REsume')
out = Path(r'C:\Users\USER\Downloads\FinalYearProject\pdf_text_extracted')
out.mkdir(exist_ok=True)

for p in sorted(root.glob('*.pdf')):
    doc = fitz.open(p)
    text = ''
    for i, page in enumerate(doc):
        text += f'\n--- page {i+1} ---\n' + page.get_text('text')
    doc.close()
    (out / (p.stem + '.txt')).write_text(text, encoding='utf-8')
    print(f'{p.name}: {len(text)} chars')
"""Audit PPTX slides for layout issues."""
import sys
sys.path.insert(0, '.')

from pptx import Presentation

prs = Presentation('AI_Digital_Twin_Enhanced_Presentation.pptx')
SLIDE_W = 13.333 * 914400  # in EMU
SLIDE_H = 7.5 * 914400

print(f'Total slides: {len(prs.slides)}')
print(f'Slide dimensions: {SLIDE_W/914400:.3f}" x {SLIDE_H/914400:.3f}"')
print()

issues = []

for i, slide in enumerate(prs.slides, 1):
    shapes_info = []
    for sh in slide.shapes:
        try:
            name = sh.name if hasattr(sh, 'name') else '?'
            t = sh.top
            l = sh.left
            w = sh.width
            h = sh.height
            b = t + h
            r = l + w
            shapes_info.append((name, l, t, w, h, b, r))
            # check boundaries: allow 0.1" margin
            if b > SLIDE_H + 91440 or r > SLIDE_W + 91440:
                issues.append(f'Slide {i}: {name} overflows at ({r/914400:.1f}", {b/914400:.1f}")')
        except Exception as e:
            pass
    print(f'Slide {i}: {len(shapes_info)} shapes')
    for name, l, t, w, h, b, r in shapes_info[:10]:
        flag = ''
        if b > SLIDE_H + 91440 or r > SLIDE_W + 91440:
            flag = ' OVERFLOW'
        print(f'  {name}: ({l/914400:.2f}", {t/914400:.2f}") size=({w/914400:.2f}"x{h/914400:.2f}"){flag}')

print()
print("=== ISSUES FOUND ===")
for issue in issues:
    print(issue)

if not issues:
    print("No major overflow issues detected.")
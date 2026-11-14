import pathlib
content = pathlib.Path("new_homepage.txt").read_text(encoding='utf-8')
pathlib.Path("frontend_web/src/app/page.tsx").write_text(content, encoding='utf-8')
print('Written successfully, length:', len(content))
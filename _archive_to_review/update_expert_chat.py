import pathlib

c = pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').read_text(encoding='utf-8')

# Replace the background classes for Digital Twin aesthetic
c = c.replace(
    'min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors',
    'min-h-screen bg-digital-twin transition-colors'
)

# Update header to glassmorphism
c = c.replace(
    '<header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50">',
    '<header className="bg-white/5 dark:bg-slate-900/50 backdrop-blur-md border-b border-white/10 dark:border-slate-800/50 sticky top-0 z-50">'
)

# Update nav links to glassmorphism style
c = c.replace(
    'className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"',
    'className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-slate-800/50 rounded-lg transition-colors"'
)

# Update active nav link (purple for expert chat)
c = c.replace(
    'className="px-4 py-2 text-sm font-medium text-purple-600 dark:text-purple-400"',
    'className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-purple-500/20 rounded-lg"'
)

pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').write_text(c, encoding='utf-8')
print('Part 1 done')
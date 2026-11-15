import pathlib

c = pathlib.Path('frontend_web/src/app/calendar/page.tsx').read_text(encoding='utf-8')

# Update CTA text
c = c.replace(
    'className="text-lg font-semibold text-purple-900 dark:text-purple-100"',
    'className="text-lg font-semibold text-purple-300"'
)
c = c.replace(
    'className="text-purple-700 dark:text-purple-300"',
    'className="text-purple-400"'
)

# Update the CTA section
c = c.replace(
    'className="mt-10 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-xl p-6 animate-slide-up"',
    'className="mt-10 glass-card border-purple-500/30 p-6 animate-slide-up"'
)

# Update no-data state - first return block
c = c.replace(
    'className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors">',
    'className="min-h-screen bg-digital-twin transition-colors">'
)
c = c.replace(
    '<header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50">',
    '<header className="bg-white/5 dark:bg-slate-900/50 backdrop-blur-md border-b border-white/10 dark:border-slate-800/50 sticky top-0 z-50">'
)
c = c.replace(
    'className="text-4xl font-bold text-slate-900 dark:text-white mb-4"',
    'className="text-4xl font-bold text-white mb-4"'
)
c = c.replace(
    'className="text-xl text-slate-600 dark:text-slate-300 mb-8 max-w-2xl mx-auto"',
    'className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto"'
)

# Update the empty state icon bg
c = c.replace(
    'className="w-20 h-20 mx-auto mb-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center"',
    'className="w-20 h-20 mx-auto mb-6 rounded-full bg-blue-500/20 flex items-center justify-center"'
)

pathlib.Path('frontend_web/src/app/calendar/page.tsx').write_text(c, encoding='utf-8')
print('Part 4 done')
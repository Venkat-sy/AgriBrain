import pathlib

c = pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').read_text(encoding='utf-8')

# Update progress indicator background
c = c.replace(
    '<div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">',
    '<div className="glass-card border-b border-white/10">'
)

# Update main heading
c = c.replace(
    'className="text-3xl font-bold text-slate-900 dark:text-white mb-2"',
    'className="text-3xl font-bold text-white mb-2"'
)
c = c.replace(
    'className="text-slate-600 dark:text-slate-400"',
    'className="text-slate-300"'
)

# Update context indicator card
c = c.replace(
    'className="mb-6 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-4"',
    'className="mb-6 glass-card p-4 card-hover"'
)

# Update context indicator icon bg
c = c.replace(
    'className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center"',
    'className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center"'
)

# Update context indicator text
c = c.replace(
    'className="text-lg font-semibold text-slate-900 dark:text-white"',
    'className="text-lg font-semibold text-white"'
)
c = c.replace(
    'className="text-sm text-slate-600 dark:text-slate-400"',
    'className="text-sm text-slate-300"'
)

# Update context badge
c = c.replace(
    'className="ml-auto px-3 py-1 text-sm font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full"',
    'className="ml-auto px-3 py-1 text-sm font-medium bg-green-500/20 text-green-400 rounded-full"'
)

# Update details/summary text
c = c.replace(
    'className="flex items-center justify-between cursor-pointer text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"',
    'className="flex items-center justify-between cursor-pointer text-sm text-slate-300 hover:text-white"'
)

# Update pre/code block
c = c.replace(
    'className="mt-3 p-4 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-600 dark:text-slate-300 overflow-x-auto whitespace-pre-wrap"',
    'className="mt-3 p-4 glass-card border-white/10 text-xs text-slate-300 overflow-x-auto whitespace-pre-wrap"'
)

pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').write_text(c, encoding='utf-8')
print('Part 2 done')
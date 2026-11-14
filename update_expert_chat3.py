import pathlib

c = pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').read_text(encoding='utf-8')

# Update Quick Action Buttons card
c = c.replace(
    'className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6"',
    'className="glass-card p-6 card-hover"'
)

# Update quick action heading
c = c.replace(
    'className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2"',
    'className="text-lg font-semibold text-white mb-4 flex items-center gap-2"'
)

# Update quick action buttons
c = c.replace(
    'className="w-full text-left p-3 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors text-sm text-slate-700 dark:text-slate-300"',
    'className="w-full text-left p-3 glass-card border-white/10 hover:bg-white/10 transition-colors text-sm text-slate-300"'
)

# Update Context Summary Cards card
c = c.replace(
    'className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6"',
    'className="glass-card p-6 card-hover"'
)

c = c.replace(
    'className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2"',
    'className="text-lg font-semibold text-white mb-4 flex items-center gap-2"'
)

pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').write_text(c, encoding='utf-8')
print('Part 3 done')
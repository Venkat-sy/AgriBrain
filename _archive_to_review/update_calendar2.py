import pathlib

c = pathlib.Path('frontend_web/src/app/calendar/page.tsx').read_text(encoding='utf-8')

# Update progress indicator background
c = c.replace(
    '<div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">',
    '<div className="glass-card border-b border-white/10">'
)

# Update main content cards - summary cards
c = c.replace(
    'className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6"',
    'className="glass-card p-6 card-hover"'
)

# Update timeline cards
c = c.replace(
    'className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden relative"',
    'className="glass-card overflow-hidden relative card-hover"'
)

# Update timeline connector
c = c.replace(
    'className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700"',
    'className="absolute left-6 top-0 bottom-0 w-0.5 bg-white/10 dark:bg-white/5"'
)

# Update timeline marker background
c = c.replace(
    'className={`w-12 h-12 rounded-full flex items-center justify-center ${getStageColor(stage.stage)} border-4 border-white dark:border-slate-800 shadow-lg`}',
    'className={`w-12 h-12 rounded-full flex items-center justify-center ${getStageColor(stage.stage)} border-4 border-white/20 dark:border-slate-800/50 shadow-xl`}'
)

# Update stat cards in timeline
c = c.replace(
    'className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg"',
    'className="p-3 glass-card border-blue-500/20"'
)
c = c.replace(
    'className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"',
    'className="p-3 glass-card border-green-500/20"'
)
c = c.replace(
    'className="p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg"',
    'className="p-3 glass-card border-purple-500/20"'
)

pathlib.Path('frontend_web/src/app/calendar/page.tsx').write_text(c, encoding='utf-8')
print('Part 2 done')
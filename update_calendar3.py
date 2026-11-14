import pathlib

c = pathlib.Path('frontend_web/src/app/calendar/page.tsx').read_text(encoding='utf-8')

# Update text colors for headings
c = c.replace(
    'className="text-3xl font-bold text-slate-900 dark:text-white mb-2"',
    'className="text-3xl font-bold text-white mb-2"'
)
c = c.replace(
    'className="text-slate-600 dark:text-slate-400"',
    'className="text-slate-300"'
)
c = c.replace(
    'className="text-xl font-bold text-slate-900 dark:text-white"',
    'className="text-xl font-bold text-white"'
)
c = c.replace(
    'className="text-slate-600 dark:text-slate-300 mb-4"',
    'className="text-slate-300 mb-4"'
)
c = c.replace(
    'className="text-xs text-blue-700 dark:text-blue-300 mb-1"',
    'className="text-xs text-blue-400 mb-1"'
)
c = c.replace(
    'className="font-semibold text-blue-900 dark:text-blue-100"',
    'className="font-semibold text-blue-300"'
)
c = c.replace(
    'className="text-xs text-green-700 dark:text-green-300 mb-1"',
    'className="text-xs text-green-400 mb-1"'
)
c = c.replace(
    'className="font-semibold text-green-900 dark:text-green-100"',
    'className="font-semibold text-green-300"'
)
c = c.replace(
    'className="text-xs text-purple-700 dark:text-purple-300 mb-1"',
    'className="text-xs text-purple-400 mb-1"'
)
c = c.replace(
    'className="font-semibold text-purple-900 dark:text-purple-100 text-sm"',
    'className="font-semibold text-purple-300 text-sm"'
)
c = c.replace(
    'className="text-sm font-semibold text-slate-900 dark:text-white mb-2"',
    'className="text-sm font-semibold text-white mb-2"'
)
c = c.replace(
    'className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400"',
    'className="flex items-center gap-2 text-sm text-slate-300"'
)

pathlib.Path('frontend_web/src/app/calendar/page.tsx').write_text(c, encoding='utf-8')
print('Part 3 done')
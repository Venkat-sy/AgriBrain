import pathlib

c = pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').read_text(encoding='utf-8')

# Update context summary cards - crop
c = c.replace(
    'className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"',
    'className="flex items-center gap-3 p-3 glass-card border-green-500/20"'
)

c = c.replace(
    'className="text-xs text-green-700 dark:text-green-300"',
    'className="text-xs text-green-400"'
)
c = c.replace(
    'className="font-medium text-green-900 dark:text-green-100 capitalize"',
    'className="font-medium text-green-300 capitalize"'
)

# Update context summary cards - location/soil
c = c.replace(
    'className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg"',
    'className="flex items-center gap-3 p-3 glass-card border-blue-500/20"'
)

c = c.replace(
    'className="text-xs text-blue-700 dark:text-blue-300"',
    'className="text-xs text-blue-400"'
)
c = c.replace(
    'className="font-medium text-blue-900 dark:text-blue-100"',
    'className="font-medium text-blue-300"'
)

# Update context summary cards - simulation
c = c.replace(
    'className="flex items-center gap-3 p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg"',
    'className="flex items-center gap-3 p-3 glass-card border-purple-500/20"'
)

c = c.replace(
    'className="text-xs text-purple-700 dark:text-purple-300"',
    'className="text-xs text-purple-400"'
)
c = c.replace(
    'className="font-medium text-purple-900 dark:text-purple-100"',
    'className="font-medium text-purple-300"'
)

# Update context summary cards - calendar
c = c.replace(
    'className="flex items-center gap-3 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg"',
    'className="flex items-center gap-3 p-3 glass-card border-amber-500/20"'
)

pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').write_text(c, encoding='utf-8')
print('Part 4 done')
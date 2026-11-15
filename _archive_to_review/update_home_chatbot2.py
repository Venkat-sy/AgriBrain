import pathlib

c = pathlib.Path('frontend_web/src/components/HomeChatbot.tsx').read_text(encoding='utf-8')

# Update suggested questions section
c = c.replace(
    'className="px-4 pb-2 border-t border-white/10 dark:border-slate-700/50"',
    'className="px-4 pb-2 border-t border-white/10"'
)

c = c.replace(
    'className="text-center text-slate-500 dark:text-slate-400 py-4 mb-2"',
    'className="text-center text-slate-400 py-4 mb-2"'
)

c = c.replace(
    'className="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium"',
    'className="text-xs text-slate-500 mb-2 font-medium"'
)

# Update suggested question buttons
c = c.replace(
    'className="text-xs px-3 py-1.5 bg-green-500/10 dark:bg-green-900/20 text-green-600 dark:text-green-400 border border-green-200 dark:border-green-800 rounded-full hover:bg-green-100 dark:hover:bg-green-900/40 transition-colors"',
    'className="text-xs px-3 py-1.5 bg-green-500/10 text-green-400 border border-green-500/20 rounded-full hover:bg-green-500/20 transition-colors"'
)

# Update connection error banner
c = c.replace(
    'className="px-4 py-3 border-t border-white/10 dark:border-slate-700/50 bg-red-500/5 dark:bg-red-900/10"',
    'className="px-4 py-3 border-t border-white/10 bg-red-500/10"'
)

c = c.replace(
    'className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400"',
    'className="flex items-center gap-2 text-sm text-red-400"'
)

c = c.replace(
    'className="ml-auto px-3 py-1 text-xs font-medium text-red-600 dark:text-red-400 bg-red-500/10 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-full hover:bg-red-500/20 transition-colors"',
    'className="ml-auto px-3 py-1 text-xs font-medium text-red-400 bg-red-500/20 border border-red-500/30 rounded-full hover:bg-red-500/30 transition-colors"'
)

# Update input area
c = c.replace(
    'className="px-4 py-3 border-t border-white/10 dark:border-slate-700/50 bg-slate-50/50 dark:bg-slate-800/50"',
    'className="px-4 py-3 border-t border-white/10 bg-white/5"'
)

pathlib.Path('frontend_web/src/components/HomeChatbot.tsx').write_text(c, encoding='utf-8')
print('Part 2 done')
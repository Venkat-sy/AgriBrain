import pathlib

c = pathlib.Path('frontend_web/src/components/ChatAssistant.tsx').read_text(encoding='utf-8')

# Update header border color
c = c.replace(
    'border-b border-white/10 dark:border-slate-700/50',
    'border-b border-white/10'
)

# Update header text colors
c = c.replace(
    'className="font-bold text-lg text-slate-900 dark:text-white"',
    'className="font-bold text-lg text-white"'
)
c = c.replace(
    'className="text-xs text-slate-500 dark:text-slate-400"',
    'className="text-xs text-slate-400"'
)

# Update retry button colors
c = c.replace(
    'className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-full hover:bg-amber-100 dark:hover:bg-amber-900/40 transition-colors"',
    'className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-amber-400 bg-amber-500/20 border border-amber-500/30 rounded-full hover:bg-amber-500/30 transition-colors"'
)

# Update user message avatar
c = c.replace(
    'className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${\n                msg.role === "user"\n                  ? "bg-blue-500/20"\n                  : "bg-green-500/20"\n              }`}',
    'className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${\n                msg.role === "user"\n                  ? "bg-blue-500/20"\n                  : "bg-green-500/20"\n              }`}'
)

# Update user message bubble
c = c.replace(
    'className={`px-4 py-3 rounded-2xl ${\n                  msg.role === "user"\n                    ? "bg-blue-500/10 text-slate-900 dark:text-blue-100 rounded-br-sm"\n                    : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-sm"\n                }`}',
    'className={`px-4 py-3 rounded-2xl ${\n                  msg.role === "user"\n                    ? "bg-blue-500/10 text-white rounded-br-sm"\n                    : "glass-card text-white rounded-bl-sm border-white/10"\n                }`}'
)

# Update timestamp color
c = c.replace(
    'className="text-[10px] text-slate-400 px-1"',
    'className="text-[10px] text-slate-500 px-1"'
)

# Update typing indicator
c = c.replace(
    'className="bg-slate-100 dark:bg-slate-800 rounded-2xl rounded-bl-sm px-4 py-3"',
    'className="glass-card rounded-2xl rounded-bl-sm px-4 py-3 border-white/10"'
)

c = c.replace(
    'className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0ms]"',
    'className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:0ms]"'
)
c = c.replace(
    'className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:150ms]"',
    'className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:150ms]"'
)
c = c.replace(
    'className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:300ms]"',
    'className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:300ms]"'
)

pathlib.Path('frontend_web/src/components/ChatAssistant.tsx').write_text(c, encoding='utf-8')
print('Part 1 done')
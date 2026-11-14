import pathlib

# Fix calendar page
c = pathlib.Path('frontend_web/src/app/calendar/page.tsx').read_text(encoding='utf-8')

# Fix remaining text-slate-900 dark:text-white - check where they are
# These might be in the no-data state or other places
c = c.replace(
    'text-slate-900 dark:text-white',
    'text-white'
)

# Fix bg-slate-800/50
c = c.replace(
    'bg-slate-800/50',
    'bg-white/5'
)

pathlib.Path('frontend_web/src/app/calendar/page.tsx').write_text(c, encoding='utf-8')
print('Fixed calendar')

# Fix expert-chat page
c = pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').read_text(encoding='utf-8')

c = c.replace(
    'text-slate-900 dark:text-white',
    'text-white'
)

c = c.replace(
    'bg-slate-800/50',
    'bg-white/5'
)

pathlib.Path('frontend_web/src/app/expert-chat/page.tsx').write_text(c, encoding='utf-8')
print('Fixed expert-chat')

# Fix ChatAssistant.tsx
c = pathlib.Path('frontend_web/src/components/ChatAssistant.tsx').read_text(encoding='utf-8')

c = c.replace(
    'border-slate-700',
    'border-white/10'
)
c = c.replace(
    'border-slate-200',
    'border-white/10'
)

# The text-slate-900 dark:text-white in ChatAssistant is in the inputClass which we already fixed
# But let's check if there are any remaining
c = c.replace(
    'text-slate-900 dark:text-white',
    'text-white'
)

pathlib.Path('frontend_web/src/components/ChatAssistant.tsx').write_text(c, encoding='utf-8')
print('Fixed ChatAssistant')

# Fix HomeChatbot.tsx
c = pathlib.Path('frontend_web/src/components/HomeChatbot.tsx').read_text(encoding='utf-8')

c = c.replace(
    'border-slate-700',
    'border-white/10'
)
c = c.replace(
    'border-slate-200',
    'border-white/10'
)

c = c.replace(
    'text-slate-900 dark:text-white',
    'text-white'
)

pathlib.Path('frontend_web/src/components/HomeChatbot.tsx').write_text(c, encoding='utf-8')
print('Fixed HomeChatbot')

print('All done')
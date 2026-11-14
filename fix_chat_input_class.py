import pathlib

for fname in ['ChatAssistant.tsx', 'HomeChatbot.tsx']:
    c = pathlib.Path(f'frontend_web/src/components/{fname}').read_text(encoding='utf-8')
    
    # Fix inputClass - replace text-slate-900 dark:text-white with text-white
    c = c.replace(
        'text-slate-900 dark:text-white placeholder-slate-400',
        'text-white placeholder-slate-500'
    )
    
    # Also fix dark:bg-slate-800/30 to bg-white/5 for consistency
    c = c.replace(
        'dark:bg-slate-800/30',
        'bg-white/5'
    )
    
    # Fix border color
    c = c.replace(
        'dark:border-slate-700/50',
        'border-white/10'
    )
    
    pathlib.Path(f'frontend_web/src/components/{fname}').write_text(c, encoding='utf-8')
    print(f'Fixed {fname}')

print('Done')
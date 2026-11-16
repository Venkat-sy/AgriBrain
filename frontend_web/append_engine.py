import os
os.chdir('C:/Users/USER/Downloads/FinalYearProject/frontend_web')
with open('src/app/simulate/page.tsx', 'a', encoding='utf-8') as f:
    f.write(open('engine_content.txt', 'r', encoding='utf-8').read())
print('Done')
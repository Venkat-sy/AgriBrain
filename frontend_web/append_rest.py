import os
os.chdir(r'C:/Users/USER/Downloads/FinalYearProject/frontend_web')
rest = open('rest_content.txt', 'r', encoding='utf-8').read()
with open('src/app/simulate/page.tsx', 'a', encoding='utf-8') as f:
    f.write(rest)
print('Appended')
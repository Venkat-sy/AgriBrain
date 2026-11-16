import os
os.chdir('C:/Users/USER/Downloads/FinalYearProject/frontend_web')
content = open('src/app/simulate/page.tsx', 'r', encoding='utf-8').read()
# Component logic already in content - just verifying
print(len(content), 'chars in file')
print('File read successfully')
import os
os.chdir(r'C:/Users/USER/Downloads/FinalYearProject/frontend_web')
text = open('src/app/simulate/page.tsx', 'r', encoding='utf-8').read()
print('File length:', len(text))
print('Ends with:', repr(text[-300:]))
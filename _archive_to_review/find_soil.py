import os
files = []
for root, dirs, filenames in os.walk('.'):
  for f in filenames:
    if 'soil' in f.lower() or 'SoilGrids' in f:
      files.append(os.path.join(root, f))
for f in files: print(f)
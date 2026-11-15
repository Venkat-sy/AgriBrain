import os
print(os.path.isdir('soil'))
if os.path.isdir('soil'):
  for root, dirs, filenames in os.walk('soil'):
    for f in filenames:
      print(os.path.join(root, f))
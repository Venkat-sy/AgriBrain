import os
for f in ['master_agri_dataset_v2.csv', 'coverage_matrix.csv', 'COVERAGE_MATRIX_SUMMARY.md']:
    if os.path.exists(f):
        print(f'{f}: {os.path.getsize(f)} bytes')
    else:
        print(f'{f}: NOT FOUND')
import json

with open('processed/icrisat_mapping.json') as f:
    m = json.load(f)

print("First 10 entries:")
i = 0
for k in m:
    print(k, m[k])
    i += 1
    if i >= 10:
        break

# Check if our manual corrections are in the mapping
test_keys = [
    'KHARGONE / WEST NIMAR|MADHYA PRADESH',
    'KHANDWA / EAST NIMAR|MADHYA PRADESH',
    'NARSINGHPUR|MADHYA PRADESH',
    'SEONI / SHIVANI|MADHYA PRADESH',
]
for k in test_keys:
    if k in m:
        print(f"Found: {k} -> {m[k]}")
    else:
        print(f"NOT FOUND: {k}")
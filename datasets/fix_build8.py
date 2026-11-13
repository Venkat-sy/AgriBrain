with open('build_geospatial_and_master.py', 'r') as f:
    content = f.read()

# Find and remove the problematic lines
idx = content.find("# Add crop agronomy features   # Rename the rainfall column")
if idx >= 0:
    # Find the next "# Add crop agronomy features" after this
    idx2 = content.find("\n\n    # Add crop agronomy features\n", idx)
    if idx2 >= 0:
        new_content = content[:idx] + content[idx2:]
        with open('build_geospatial_and_master.py', 'w') as f:
            f.write(new_content)
        print('Fixed - removed duplicate section')
    else:
        print('Second marker not found')
else:
    print('First marker not found')
with open("page.tsx", "r") as f:
    content = f.read()
idx = content.find("activeTab === \"input\"")
if idx >= 0:
    print(repr(content[max(0,idx-200):idx+500]))

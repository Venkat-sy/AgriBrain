with open(r'C:/Users/USER/Downloads/FinalYearProject/frontend_web/src/app/simulate/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Read the exact text from exact.txt
with open('exact.txt', 'r', encoding='utf-8') as f:
    old_text = f.read()

print(f"Old text length: {len(old_text)}")
print(f"Old text starts with: {repr(old_text[:50])}")

new_text = (
    "</Card>\n"
    "\n"
    "              </>)\n"
    "            ) : (\n"
    "              <>\n"
    "                {/* Empty State */}\n"
    "                <Card className=\"h-full min-h-[500px] flex flex-col items-center justify-center\">\n"
    "                  <div className=\"text-center\">\n"
    "                    <Cpu className=\"w-16 h-16 text-slate-300 mx-auto mb-4\" />\n"
    "                    <h3 className=\"text-xl font-semibold text-slate-700 mb-2\">Ready to Simulate</h3>\n"
    "                    <p className=\"text-slate-500 mb-6 max-w-sm\">\n"
    "                      Pin your farm location on the map, configure parameters, and run the digital twin engine\n"
    "                      to get AI-scored crop recommendations with SHAP explainability.\n"
    "                    </p>\n"
    "                    <div className=\"grid grid-cols-3 gap-4 text-sm text-center\">\n"
    "                      <div className=\"p-3 bg-slate-50 rounded-lg\">\n"
    "                        <p className=\"text-2xl font-bold text-emerald-600\">45</p>\n"
    "                        <p className=\"text-slate-500\">Crops in Database</p>\n"
    "                      </div>\n"
    "                      <div className=\"p-3 bg-slate-50 rounded-lg\">\n"
    "                        <p className=\"text-2xl font-bold text-emerald-600\">8</p>\n"
    "                        <p className=\"text-slate-500\">Indian Soil Profiles</p>\n"
    "                      </div>\n"
    "                      <div className=\"p-3 bg-slate-50 rounded-lg\">\n"
    "                        <p className=\"text-2xl font-bold text-emerald-600\">5</p>\n"
    "                        <p className=\"text-slate-500\">Agro-Climatic Zones</p>\n"
    "                      </div>\n"
    "                    </div>\n"
    "                  </div>\n"
    "                </Card>\n"
    "              </>\n"
    "            )}\n"
    "\n"
    "       </div>\n"
    "        </div>\n"
    "      </div>\n"
    "    </main>\n"
    "  );\n"
    "}"
)

if old_text in text:
    text = text.replace(old_text, new_text)
    with open(r'C:/Users/USER/Downloads/FinalYearProject/frontend_web/src/app/simulate/page.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Fixed successfully!')
else:
    print('Text not found!')
    # Check if it's a subset
    idx = text.rfind('</Card>')
    if idx >= 0:
        print('FOUND:', repr(text[idx-100:idx+500]))

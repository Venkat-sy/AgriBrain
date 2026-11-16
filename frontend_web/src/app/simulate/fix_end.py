with open(r'C:/Users/USER/Downloads/FinalYearProject/frontend_web/src/app/simulate/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Find and replace the problematic section - exact current content (without the </>) in false branch)
old_text = """              </Card>              </>)
            ) : (
              {/* Empty State */}
              <Card className="h-full min-h-[500px] flex flex-col items-center justify-center">
                <div className="text-center">
                  <Cpu className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-700 mb-2">Ready to Simulate</h3>
                  <p className="text-slate-500 mb-6 max-w-sm">
                    Pin your farm location on the map, configure parameters, and run the digital twin engine
                    to get AI-scored crop recommendations with SHAP explainability.
                  </p>
                  <div className="grid grid-cols-3 gap-4 text-sm text-center">
                    <div className="p-3 bg-slate-50 rounded-lg">
                      <p className="text-2xl font-bold text-emerald-600">45</p>
                      <p className="text-slate-500">Crops in Database</p>
                    </div>
                    <div className="p-3 bg-slate-50 rounded-lg">
                      <p className="text-2xl font-bold text-emerald-600">8</p>
                      <p className="text-slate-500">Indian Soil Profiles</p>
                    </div>
                    <div className="p-3 bg-slate-50 rounded-lg">
                      <p className="text-2xl font-bold text-emerald-600">5</p>
                      <p className="text-slate-500">Agro-Climatic Zones</p>
                    </div>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}"""

new_text = """              </Card>
              </>)
            ) : (
              <>
                {/* Empty State */}
                <Card className="h-full min-h-[500px] flex flex-col items-center justify-center">
                  <div className="text-center">
                    <Cpu className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-slate-700 mb-2">Ready to Simulate</h3>
                    <p className="text-slate-500 mb-6 max-w-sm">
                      Pin your farm location on the map, configure parameters, and run the digital twin engine
                      to get AI-scored crop recommendations with SHAP explainability.
                    </p>
                    <div className="grid grid-cols-3 gap-4 text-sm text-center">
                      <div className="p-3 bg-slate-50 rounded-lg">
                        <p className="text-2xl font-bold text-emerald-600">45</p>
                        <p className="text-slate-500">Crops in Database</p>
                      </div>
                      <div className="p-3 bg-slate-50 rounded-lg">
                        <p className="text-2xl font-bold text-emerald-600">8</p>
                        <p className="text-slate-500">Indian Soil Profiles</p>
                      </div>
                      <div className="p-3 bg-slate-50 rounded-lg">
                        <p className="text-2xl font-bold text-emerald-600">5</p>
                        <p className="text-slate-500">Agro-Climatic Zones</p>
                      </div>
                    </div>
                  </div>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}"""

if old_text in text:
    text = text.replace(old_text, new_text)
    with open(r'C:/Users/USER/Downloads/FinalYearProject/frontend_web/src/app/simulate/page.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Fixed successfully!')
else:
    print('Text not found!')
    # Let's find what's actually there
    idx = text.rfind('</Card>')
    if idx >= 0:
        print('FOUND:', repr(text[idx-100:idx+500]))
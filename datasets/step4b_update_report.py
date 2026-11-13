import pandas as pd
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# STEP 4b: Update DATA_COVERAGE_REPORT.md
# ============================================================

with open('temp_all_year_dfs.pkl', 'rb') as f:
    all_year_dfs = pickle.load(f)

annual = pd.read_pickle('temp_annual.pkl')
coverage_df = pd.read_pickle('temp_coverage_df.pkl')
full_combined = pd.read_pickle('temp_combined_full.pkl')

print("Updating DATA_COVERAGE_REPORT.md...")

with open('DATA_COVERAGE_REPORT.md', 'r') as f:
    report = f.read()

# Check if section exists
if "## Rainfall Data Integration (2025-2026) - NEW" in report:
    print("Found existing section, replacing...")
else:
    print("Section not found, will append")

# Read new section from a separate file to avoid size limits
with open('report_new_section.md', 'r') as f:
    new_section = f.read()

# Format with actual values
new_section = new_section.format(
    total_records=f"{len(full_combined):,}",
    y2021=f"{len(all_year_dfs[0]):,}",
    y2022=f"{len(all_year_dfs[1]):,}",
    y2023=f"{len(all_year_dfs[2]):,}",
    y2024=f"{len(all_year_dfs[3]):,}",
    annual_records=len(annual),
    coverage_districts=len(coverage_df)
)

# Replace or append
start_idx = report.find("## Rainfall Data Integration (2025-2026) - NEW")
if start_idx >= 0:
    end_idx = report.find("\n## ", start_idx + 1)
    if end_idx < 0:
        end_idx = len(report)
    updated_report = report[:start_idx] + new_section + report[end_idx:]
else:
    updated_report = report + new_section

with open('DATA_COVERAGE_REPORT.md', 'w') as f:
    f.write(updated_report)
print("Updated DATA_COVERAGE_REPORT.md")
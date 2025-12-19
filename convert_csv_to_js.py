import os
import sys
import json
import csv

# Read the CSV and convert to JSON for the HTML
csv_file = 'mondoffice_complete_classification.csv'
output_file = 'mondoffice_data.js'

campaigns = []

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            campaigns.append({
                'id': row['Campaign_ID'],
                'name': row['Campaign_Name'],
                'type': row['Type'],
                'cost': float(row['Cost_EUR']),
                'conversions': float(row['Total_Conversions']),
                'value': float(row['Conv_Value_EUR']),
                'roas': float(row['ROAS']),
                'purchases': float(row['Purchases']),
                'newB2B': float(row['New_B2B']),
                'newB2BRatio': float(row['New_B2B_Ratio'])
            })
        except (ValueError, KeyError) as e:
            print(f"Skipping row due to error: {e}")
            continue

# Write as JavaScript file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('const campaignsData = ')
    json.dump(campaigns, f, indent=2, ensure_ascii=False)
    f.write(';')

print(f"✅ Converted {len(campaigns)} campaigns to JavaScript")
print(f"   Output: {output_file}")

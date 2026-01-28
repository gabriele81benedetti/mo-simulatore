import os
import sys
import csv
from datetime import date, timedelta

# Add the google-ads-mcp directory to sys.path
# Use absolute path relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_path = os.path.join(current_dir, "..", "..", "google_ads_mcp")
sys.path.insert(0, mcp_path)

# Set the developer token
os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"] = "z3AZMWAW-b5VXiT0zl3ZMw"
os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"] = "1215695365"

# Bypass package structure for standalone execution
tools_path = os.path.join(mcp_path, "ads_mcp", "tools")
sys.path.insert(0, tools_path)

try:
    from search import search
    
    customer_id = "5668436290"
    
    print(f"🔍 ANALISI COMPLETA MONDOFFICE - Classificazione Campagne (CORRETTA)")
    print("=" * 120)

    today = date.today()
    end_date = date(2025, 12, 31)
    start_date = date(2025, 9, 26)
    
    date_range_str = f"segments.date BETWEEN '{start_date}' AND '{end_date}'"
    
    # 1. Fetch Campaign Costs
    print("Fetching Campaign Costs...")
    cost_results = search(
        customer_id=customer_id,
        fields=[
            "campaign.id", 
            "campaign.name", 
            "metrics.cost_micros",
            "metrics.conversions",
            "metrics.conversions_value"
        ],
        resource="campaign",
        conditions=[
            "campaign.status = 'ENABLED'",
            "metrics.cost_micros > 0",
            date_range_str
        ]
    )
    
    campaign_data = {}
    
    for row in cost_results:
        c_id = str(row['campaign.id'])
        
        # BRAND_Exact is VALID (confirmed by user total 35M)
        # if c_id == "140976423": ...
            
        c_name = row['campaign.name']
        cost = int(row.get('metrics.cost_micros', 0)) / 1_000_000
        total_conv_raw = float(row.get('metrics.conversions', 0))
        total_value_raw = float(row.get('metrics.conversions_value', 0))
        
        campaign_data[c_id] = {
            'name': c_name,
            'total_cost': cost,
            'total_conversions': total_conv_raw, 
            'total_value': total_value_raw,       
            'conversion_breakdown': {}
        }

    # 2. Fetch Conversion Data by Action
    print("Fetching Conversion Breakdown...")
    
    conv_results = search(
        customer_id=customer_id,
        fields=[
            "campaign.id", 
            "metrics.conversions", 
            "metrics.conversions_value",
            "segments.conversion_action_name"
        ],
        resource="campaign",
        conditions=[
            "campaign.status = 'ENABLED'",
            "metrics.conversions > 0",
            date_range_str
        ]
    )
    
    for row in conv_results:
        c_id = str(row['campaign.id'])
        
        if c_id not in campaign_data:
             continue
              
        conv_action = row['segments.conversion_action_name']
        conversions = float(row.get('metrics.conversions', 0))
        value = float(row.get('metrics.conversions_value', 0))
        
        if conv_action not in campaign_data[c_id]['conversion_breakdown']:
            campaign_data[c_id]['conversion_breakdown'][conv_action] = {
                'conversions': 0,
                'value': 0
            }
        
        campaign_data[c_id]['conversion_breakdown'][conv_action]['conversions'] += conversions
        campaign_data[c_id]['conversion_breakdown'][conv_action]['value'] += value

    # 3. Classify campaigns
    print("\nClassifying campaigns...\n")
    
    classified_campaigns = []
    
    for c_id, data in campaign_data.items():
        name = data['name']
        cost = data['total_cost']
        # Use the campaign-level total value as the authoritative revenue
        final_revenue = data['total_value']
        final_conversions = data['total_conversions']
        
        # Extract specific conversion counts for classification
        purchases = 0
        new_b2b = 0
        other = 0
        
        for action, stats in data['conversion_breakdown'].items():
            conv_count = stats['conversions']
            
            # CATEGORIZATION
            # Identify NEW B2B only from GA4 stable source
            is_new_b2b = "[GA4] MONDOFFICE (web) NEW purchase B2B" in action
            # STRICT REVENUE FILTER: Only "Acquisto/Vendita" counts for Revenue
            is_main_purchase = action == "Acquisto/Vendita"
            
            if is_new_b2b:
                new_b2b += conv_count
            elif is_main_purchase:
                purchases += conv_count
            else:
                other += conv_count
            
        
        # Calculate metrics
        roas = (final_revenue / cost) if cost > 0 else 0
        cpa = (cost / final_conversions) if final_conversions > 0 else 0
        new_b2b_ratio = (new_b2b / final_conversions * 100) if final_conversions > 0 else 0
        
        # Auto-classification logic
        campaign_type = "UNKNOWN"
        suggested_strategy = "UNKNOWN"
        reasoning = ""
        
        if "NCA" in name or "_NCA" in name:
            campaign_type = "NEW_CUSTOMER_ACQUISITION"
            suggested_strategy = "tCPA (New Customer)"
            reasoning = "Nome campagna contiene NCA"
        elif "BRAND" in name:
            if new_b2b_ratio >= 30:
                campaign_type = "HYBRID"
                suggested_strategy = "tCPA (New Customer) o Dual Strategy"
                reasoning = f"Brand con {new_b2b_ratio:.0f}% nuovi clienti"
            else:
                campaign_type = "REVENUE_RETENTION"
                suggested_strategy = "tROAS"
                reasoning = "Brand principalmente retention"
        elif new_b2b_ratio >= 50:
            campaign_type = "NEW_CUSTOMER_ACQUISITION"
            suggested_strategy = "tCPA (New Customer)"
            reasoning = f"Alto ratio nuovi clienti ({new_b2b_ratio:.0f}%)"
        elif new_b2b_ratio >= 35:
            campaign_type = "HYBRID"
            suggested_strategy = "Valutare in base a target revenue"
            reasoning = f"Ratio bilanciato ({new_b2b_ratio:.0f}% nuovi)"
        elif new_b2b_ratio > 0:
            campaign_type = "REVENUE_RETENTION"
            suggested_strategy = "tROAS"
            reasoning = f"Principalmente revenue"
        elif purchases == 0 and new_b2b == 0:
            campaign_type = "LEAD_GENERATION"
            suggested_strategy = "tCPA (Lead)"
            reasoning = "Solo lead generation"
        
        classified_campaigns.append({
            'Campaign_ID': c_id,
            'Campaign_Name': name,
            'Type': campaign_type,
            'Suggested_Strategy': suggested_strategy,
            'Cost_EUR': round(cost, 2),
            'Total_Conversions': round(final_conversions, 2),
            'Conv_Value_EUR': round(final_revenue, 2),
            'ROAS': round(roas, 2),
            'CPA_EUR': round(cpa, 2),
            'Purchases': round(purchases, 2),
            'New_B2B': round(new_b2b, 2),
            'Other_Conv': round(other, 2),
            'New_B2B_Ratio': round(new_b2b_ratio, 1),
            'Reasoning': reasoning
        })
    
    # Sort by cost descending
    classified_campaigns.sort(key=lambda x: x['Cost_EUR'], reverse=True)
    
    # Export to CSV
    output_file = 'mondoffice_complete_classification.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Campaign_ID', 'Campaign_Name', 'Type', 'Suggested_Strategy', 
                      'Cost_EUR', 'Total_Conversions', 'Conv_Value_EUR', 'ROAS', 'CPA_EUR',
                      'Purchases', 'New_B2B', 'Other_Conv', 'New_B2B_Ratio', 'Reasoning']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(classified_campaigns)
    
    print(f"\n✅ Analisi completa esportata in:")
    print(f"   {output_file}")
    
    total_rev = sum(c['Conv_Value_EUR'] for c in classified_campaigns)
    total_cost_calc = sum(c['Cost_EUR'] for c in classified_campaigns)
    
    print(f"   Total Cost Calculated: €{total_cost_calc:,.2f}")
    print(f"   Total Revenue Calculated (Filtered): €{total_rev:,.2f}")

    # DEBUG: Analyze all conversion values
    print("\n--- DEBUG: Conversion Value Breakdown ---")
    global_breakdown = {}
    total_raw_value = 0
    
    for c_id, data in campaign_data.items():
        for action, stats in data['conversion_breakdown'].items():
            val = stats['value']
            total_raw_value += val
            if action not in global_breakdown:
                global_breakdown[action] = 0
            global_breakdown[action] += val
            
    print(f"   RAW TOTAL VALUE (All Actions): €{total_raw_value:,.2f}")
    print("   Breakdown by Action:")
    for action, val in global_breakdown.items():
        print(f"   - {action}: €{val:,.2f}")

except Exception as e:
    print(f"Error: {e}")

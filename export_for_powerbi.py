# export_for_powerbi.py - ✅ AUTO-CREATES FOLDERS + ERROR-PROOF
import pandas as pd
import numpy as np
import os
from pathlib import Path
from analysis import (load_stock_data, calculate_key_metrics, calculate_volatility, 
                     calculate_cumulative_returns, get_sector_performance, 
                     get_monthly_top_gainers_losers)

print("🚀 POWER BI EXPORT STARTED...")
print("=" * 50)

# ✅ AUTO-CREATE powerbi FOLDER
powerbi_dir = Path("powerbi")
powerbi_dir.mkdir(exist_ok=True)
print(f"✅ Created folder: {powerbi_dir.absolute()}")

try:
    # Load & analyze ALL data
    print("📊 Loading stock data...")
    df = load_stock_data()
    if df.empty:
        print("❌ No stock data found! Create data/csv/*.csv files")
        exit(1)
    
    print(f"✅ Loaded {len(df)} rows, {df['Symbol'].nunique()} stocks")
    
    # Calculate ALL metrics
    print("🔬 Calculating metrics...")
    green, red, summary, yearly = calculate_key_metrics(df)
    volatility = calculate_volatility(df)
    cum_returns, top5 = calculate_cumulative_returns(df)
    sector_perf = get_sector_performance(df)
    monthly = get_monthly_top_gainers_losers(df)
    
    print("✅ All metrics calculated!")
    
    # EXPORT 7 POWER BI-READY FILES
    print("\n📁 EXPORTING FILES...")
    
    # 1. RAW DATA
    df.to_csv(powerbi_dir / 'raw_stock_data.csv', index=False)
    print("✅ 1. raw_stock_data.csv")
    
    # 2. KEY METRICS
    metrics_df = pd.DataFrame([summary])
    metrics_df.to_csv(powerbi_dir / 'key_metrics.csv', index=False)
    green.to_csv(powerbi_dir / 'top_green.csv', index=False)
    red.to_csv(powerbi_dir / 'top_red.csv', index=False)
    print("✅ 2. key_metrics.csv, top_green.csv, top_red.csv")
    
    # 3. VOLATILITY
    volatility.to_csv(powerbi_dir / 'volatility.csv', index=False)
    print("✅ 3. volatility.csv")
    
    # 4. SECTOR PERFORMANCE
    sector_perf.to_csv(powerbi_dir / 'sector_performance.csv', index=False)
    print("✅ 4. sector_performance.csv")
    
    # 5. CUMULATIVE RETURNS (Top 5 stocks only)
    cum_returns.to_csv(powerbi_dir / 'cumulative_returns.csv', index=True)
    print("✅ 5. cumulative_returns.csv")
    
    # 6. MONTHLY ANALYSIS (Flattened)
    monthly_flat = []
    for month, data in monthly.items():
        gainers = data['gainers'].copy()
        gainers['Month'] = month
        gainers['Type'] = 'Gainers'
        losers = data['losers'].copy()
        losers['Month'] = month
        losers['Type'] = 'Losers'
        monthly_flat.append(pd.concat([gainers, losers]))
    
    if monthly_flat:
        monthly_df = pd.concat(monthly_flat, ignore_index=True)
        monthly_df.to_csv(powerbi_dir / 'monthly_analysis.csv', index=False)
        print("✅ 6. monthly_analysis.csv")
    else:
        print("⚠️ No monthly data")
    
    # 7. SUMMARY REPORT
    summary_report = pd.DataFrame({
        'Metric': ['Total Stocks', 'Green Stocks', 'Red Stocks', 'Avg Close', 'Avg Volume', 'Avg Return %'],
        'Value': [summary['total_stocks'], summary['green_stocks'], summary['red_stocks'],
                 f"₹{summary['avg_close_price']:.0f}", f"{summary['avg_volume']:,.0f}",
                 f"{summary['avg_yearly_return']:.1f}%"]
    })
    summary_report.to_csv(powerbi_dir / 'summary_report.csv', index=False)
    print("✅ 7. summary_report.csv")
    
    print("\n🎉 SUCCESS! ALL FILES EXPORTED!")
    print(f"📁 Folder: {powerbi_dir.absolute()}")
    print("\n📋 FILES CREATED:")
    for file in powerbi_dir.glob("*.csv"):
        print(f"   ✅ {file.name}")
    
    print("\n🚀 NEXT: Open Power BI Desktop → Get Data → Folder → Select 'powerbi' folder!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

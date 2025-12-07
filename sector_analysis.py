# sector_analysis.py
import pandas as pd
from analysis import load_stock_data, calculate_key_metrics

def analyze_sector_performance():
    """Calculate sector-wise performance"""
    df = load_stock_data()
    _, _, _, yearly_returns = calculate_key_metrics(df)
    
    # Load sector data
    sectors_df = pd.read_csv('data/sector_data.csv')
    
    # Merge sector information
    sector_performance = yearly_returns.merge(sectors_df, on='Symbol', how='left')
    
    # Calculate average return by sector
    sector_avg = sector_performance.groupby('Sector')['Yearly_Return'].mean().reset_index()
    sector_avg = sector_avg.sort_values('Yearly_Return', ascending=False)
    
    return sector_performance, sector_avg

if __name__ == "__main__":
    sector_perf, sector_avg = analyze_sector_performance()
    print("🏢 Sector Performance:")
    print(sector_avg)

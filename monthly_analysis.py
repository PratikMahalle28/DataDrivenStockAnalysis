# monthly_analysis.py
import pandas as pd
from analysis import load_stock_data
import plotly.express as px

def monthly_top_gainers_losers():
    """Generate monthly top 5 gainers and losers"""
    df = load_stock_data()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    
    monthly_results = {}
    
    for month in df['Month'].unique():
        month_data = df[df['Month'] == month]
        monthly_returns = []
        
        for symbol in month_data['Symbol'].unique():
            symbol_data = month_data[month_data['Symbol'] == symbol]
            if len(symbol_data) > 0:
                first_close = symbol_data.iloc[0]['Close']
                last_close = symbol_data.iloc[-1]['Close']
                monthly_return = (last_close - first_close) / first_close * 100
                monthly_returns.append({'Symbol': symbol, 'Monthly_Return_%': monthly_return})
        
        monthly_df = pd.DataFrame(monthly_returns)
        gainers = monthly_df.nlargest(5, 'Monthly_Return_%')
        losers = monthly_df.nsmallest(5, 'Monthly_Return_%')
        monthly_results[month] = {'gainers': gainers, 'losers': losers}
    
    return monthly_results

if __name__ == "__main__":
    results = monthly_top_gainers_losers()
    for month, data in results.items():
        print(f"\n{month}:")
        print("Top Gainers:", data['gainers'])
        print("Top Losers:", data['losers'])

# stock_analyzer.py
import pandas as pd
import numpy as np
import sqlite3
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

class StockAnalyzer:
    def __init__(self, csv_dir="data/csv"):
        self.csv_dir = csv_dir
        self.engine = create_engine('sqlite:///stocks.db')
        self.load_data()
    
    def load_data(self):
        """Load all CSV files into SQLite"""
        conn = sqlite3.connect('stocks.db')
        
        # Master table
        master_df = pd.read_csv(f"{self.csv_dir}/nifty50_master.csv")
        master_df.to_sql('stocks', conn, if_exists='replace', index=False)
        
        # Per symbol tables
        for symbol in master_df['symbol'].unique():
            symbol_df = pd.read_csv(f"{self.csv_dir}/{symbol}.csv")
            symbol_df.to_sql(symbol.lower(), conn, if_exists='replace', index=False)
        
        conn.close()
        print("✅ Data loaded to SQLite")
    
    def calculate_returns(self, symbol):
        """Calculate daily & yearly returns"""
        df = pd.read_sql(f"SELECT * FROM '{symbol.lower()}' ORDER BY date", self.engine)
        df['date'] = pd.to_datetime(df['date'])
        df['daily_return'] = df['close'].pct_change()
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
        df['volatility'] = df['daily_return'].rolling(20).std()
        df['yearly_return'] = df['cumulative_return'].iloc[-1]
        return df
    
    def get_top_green_red(self, top_n=10):
        """Top 10 Green/Red stocks"""
        results = []
        for symbol in pd.read_sql("SELECT DISTINCT symbol FROM stocks", self.engine)['symbol']:
            df = self.calculate_returns(symbol)
            yearly_return = df['yearly_return'].iloc[-1] if len(df) > 0 else 0
            results.append({'symbol': symbol, 'yearly_return': yearly_return})
        
        df_returns = pd.DataFrame(results)
        green = df_returns.nlargest(top_n, 'yearly_return')
        red = df_returns.nsmallest(top_n, 'yearly_return')
        
        return green, red
    
    def market_summary(self):
        """Market overview stats"""
        df = pd.read_sql("SELECT * FROM stocks", self.engine)
        df['date'] = pd.to_datetime(df['date'])
        df['daily_return'] = df.groupby('symbol')['close'].pct_change()
        
        green_stocks = len(df[df['daily_return'] > 0]['symbol'].unique())
        red_stocks = len(df[df['daily_return'] < 0]['symbol'].unique())
        
        return {
            'total_stocks': len(df['symbol'].unique()),
            'green_stocks': green_stocks,
            'red_stocks': red_stocks,
            'avg_close': df['close'].mean(),
            'avg_volume': df['volume'].mean()
        }
    
    def get_volatility_top(self, top_n=10):
        """Top volatile stocks"""
        results = []
        for symbol in pd.read_sql("SELECT DISTINCT symbol FROM stocks", self.engine)['symbol']:
            df = self.calculate_returns(symbol)
            vol = df['volatility'].mean()
            results.append({'symbol': symbol, 'volatility': vol})
        
        return pd.DataFrame(results).nlargest(top_n, 'volatility')
    
    def sector_performance(self, sector_file="data/sectors.csv"):
        """Sector-wise analysis"""
        sectors = pd.read_csv(sector_file)
        results = []
        
        for symbol in sectors['symbol']:
            df = self.calculate_returns(symbol)
            yearly_return = df['yearly_return'].iloc[-1] if len(df) > 0 else 0
            sector = sectors[sectors['symbol'] == symbol]['sector'].iloc[0]
            results.append({'symbol': symbol, 'sector': sector, 'yearly_return': yearly_return})
        
        df = pd.DataFrame(results)
        sector_avg = df.groupby('sector')['yearly_return'].mean().reset_index()
        return sector_avg.sort_values('yearly_return', ascending=False)
    
    def correlation_matrix(self):
        """Stock correlation heatmap data"""
        closes = pd.read_sql("""
            SELECT symbol, date, close 
            FROM stocks 
            WHERE date >= date('now', '-1 year')
        """, self.engine)
        
        pivot = closes.pivot(index='date', columns='symbol', values='close')
        return pivot.corr()

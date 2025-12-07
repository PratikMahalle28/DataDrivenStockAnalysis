import os
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

# Part 1: Data Extraction & Transformation from YAML to CSV
'''
def extract_yaml_to_csv(yaml_folder_path, output_folder):
    """
    Extracts stock data stored in nested YAML files (by month and day),
    transforms and aggregates it by stock symbol,
    then saves each symbol's full year data as a CSV.
    """
    all_data = []

    # Walk through all months and dates
    for month in os.listdir(yaml_folder_path):
        month_path = os.path.join(yaml_folder_path, month)
        if not os.path.isdir(month_path):
            continue

        for yaml_file in os.listdir(month_path):
            if not yaml_file.endswith(".yaml"):
                continue
            file_path = os.path.join(month_path, yaml_file)
            with open(file_path, "r") as f:
                daily_data = yaml.safe_load(f)

            # daily_data assumed in format {symbol: {open, close, high, low, volume}}
            # Add date info (from folder/filename if needed)
            for symbol, metrics in daily_data.items():
                record = {"symbol": symbol, "month": month, "date": yaml_file.replace(".yaml", "")}
                record.update(metrics)
                all_data.append(record)

    df = pd.DataFrame(all_data)

    # Save data per symbol
    os.makedirs(output_folder, exist_ok=True)
    for symbol, symbol_df in df.groupby("symbol"):
        symbol_df.to_csv(os.path.join(output_folder, f"{symbol}.csv"), index=False)

    return df
'''
# Part 2: Data Cleaning and Preparation

def prepare_stock_data(df):
    """
    Cleans and prepares stock data for analysis.
    Converts data types, sorts by date, fills missing values.
    """
    df['date'] = pd.to_datetime(df['month'] + "-" + df['date'], format="%b-%d")  # Adjust date parsing as necessary
    numeric_cols = ['open', 'close', 'high', 'low', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.sort_values(['symbol', 'date'], inplace=True)
    df.fillna(method='ffill', inplace=True)
    df.dropna(inplace=True)  # Drop if still missing values after fill

    return df

# Part 3: Analysis Metrics

def calculate_yearly_return(df):
    """
    Calculates yearly return per stock: (last close - first close) / first close
    """
    first_last = df.groupby('symbol').agg(first_close=('close', 'first'), last_close=('close', 'last'))
    first_last['yearly_return'] = (first_last['last_close'] - first_last['first_close']) / first_last['first_close']
    return first_last

def calculate_volatility(df):
    """
    Calculates volatility (std deviation of daily returns)
    """
    df['daily_return'] = df.groupby('symbol')['close'].pct_change()
    volatility = df.groupby('symbol')['daily_return'].std().sort_values(ascending=False)
    return volatility

def calculate_cumulative_return(df):
    """
    Calculates cumulative return over time for each stock
    """
    df['daily_return'] = df.groupby('symbol')['close'].pct_change()
    df['cumulative_return'] = df.groupby('symbol')['daily_return'].apply(lambda x: (1 + x).cumprod() - 1)
    return df

def market_summary(df):
    """
    Provides summary of green (positive yearly return) vs red stocks
    and average price and volume.
    """
    yearly_return = calculate_yearly_return(df)
    green_stocks = yearly_return[yearly_return['yearly_return'] > 0]
    red_stocks = yearly_return[yearly_return['yearly_return'] < 0]

    avg_price = df['close'].mean()
    avg_volume = df['volume'].mean()
    summary = {
        'green_count': len(green_stocks),
        'red_count': len(red_stocks),
        'avg_price': avg_price,
        'avg_volume': avg_volume
    }
    return summary

# Part 4: Sector-wise Performance

def sector_performance(df, sector_mapping_file):
    """
    Reads sector mapping CSV, joins with stock data,
    then computes average yearly return per sector.
    """
    sector_df = pd.read_csv(sector_mapping_file)  # Expected columns: symbol, sector
    yearly_return = calculate_yearly_return(df).reset_index()
    merged = pd.merge(yearly_return, sector_df, on='symbol', how='left')
    sector_avg_return = merged.groupby('sector')['yearly_return'].mean().sort_values(ascending=False)
    return sector_avg_return

# Part 5: Correlation Matrix

def stock_price_correlation(df):
    """
    Creates correlation matrix of close prices of all stocks.
    """
    pivot_df = df.pivot(index='date', columns='symbol', values='close').fillna(method='ffill').dropna(axis=1)
    corr_matrix = pivot_df.corr()
    return corr_matrix

# Part 6: Monthly Gain/Loss

def monthly_gainers_losers(df):
    """
    Calculate per-month top 5 gainers and losers based on monthly return.
    """
    df['month'] = df['date'].dt.to_period('M')
    df['monthly_return'] = df.groupby(['symbol', 'month'])['close'].pct_change()

    monthly_return = df.groupby(['symbol', 'month'])['monthly_return'].last().reset_index()

    monthly_top_gainers = monthly_return.groupby('month').apply(lambda x: x.nlargest(5, 'monthly_return')).reset_index(drop=True)
    monthly_top_losers = monthly_return.groupby('month').apply(lambda x: x.nsmallest(5, 'monthly_return')).reset_index(drop=True)

    return monthly_top_gainers, monthly_top_losers

# Part 7: Streamlit Dashboard

def streamlit_dashboard(df, sector_mapping_file):
    st.title("Nifty 50 Stock Performance Dashboard")

    yearly_returns = calculate_yearly_return(df)
    volatility = calculate_volatility(df)
    cumulative_df = calculate_cumulative_return(df)
    sector_avg_return = sector_performance(df, sector_mapping_file)
    corr_matrix = stock_price_correlation(df)
    gainers, losers = monthly_gainers_losers(df)

    # Market Summary
    summary = market_summary(df)
    st.header("Market Overview")
    st.write(f"Green Stocks: {summary['green_count']}, Red Stocks: {summary['red_count']}")
    st.write(f"Average Closing Price: {summary['avg_price']:.2f}")
    st.write(f"Average Volume: {summary['avg_volume']:.2f}")

    # Top Performers
    st.header("Top 10 Gainers & Losers Over the Year")
    top_10_gainers = yearly_returns.sort_values('yearly_return', ascending=False).head(10)
    top_10_losers = yearly_returns.sort_values('yearly_return').head(10)
    st.write("Top 10 Gainers")
    st.dataframe(top_10_gainers)
    st.write("Top 10 Losers")
    st.dataframe(top_10_losers)

    # Volatility plot
    st.header("Top 10 Most Volatile Stocks")
    top_volatility = volatility.head(10)
    fig, ax = plt.subplots()
    top_volatility.plot(kind='bar', ax=ax)
    ax.set_ylabel("Volatility (Std Dev of Daily Returns)")
    st.pyplot(fig)

    # Cumulative returns plot - Top 5 stocks
    st.header("Cumulative Returns of Top 5 Stocks")
    top_5_symbols = top_10_gainers.index[:5]
    fig, ax = plt.subplots()
    for symbol in top_5_symbols:
        subset = cumulative_df[cumulative_df['symbol'] == symbol]
        ax.plot(subset['date'], subset['cumulative_return'], label=symbol)
    ax.legend()
    ax.set_ylabel("Cumulative Return")
    st.pyplot(fig)

    # Sector-wise performance
    st.header("Average Yearly Return by Sector")
    fig, ax = plt.subplots()
    sector_avg_return.plot(kind='bar', ax=ax)
    ax.set_ylabel("Average Yearly Return")
    st.pyplot(fig)

    # Correlation Heatmap
    st.header("Stock Price Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, cmap='coolwarm', ax=ax, annot=False)
    st.pyplot(fig)

    # Monthly Gainers and Losers (example for January)
    st.header("Monthly Top 5 Gainers and Losers (Example: January)")
    jan_gainers = gainers[gainers['month'] == '2025-01']
    jan_losers = losers[losers['month'] == '2025-01']

    st.subheader("Top 5 Gainers in January")
    st.dataframe(jan_gainers)
    st.subheader("Top 5 Losers in January")
    st.dataframe(jan_losers)


if __name__ == "__main__":
    # Set paths according to your dataset locations
    yaml_folder = "path_to_yaml_data"       # Replace with your YAML data root folder path
    csv_output_folder = "stock_csv_files"   # Folder to save CSV files by symbol
    sector_file = "sector_mapping.csv"      # CSV mapping symbol to sector

    # Extract & transform
    # full_df = extract_yaml_to_csv(yaml_folder, csv_output_folder)

    # Or if CSVs already extracted, load all CSVs into one DataFrame
    csv_files = [os.path.join(csv_output_folder, f) for f in os.listdir(csv_output_folder) if f.endswith('.csv')]
    df_list = [pd.read_csv(f) for f in csv_files]
    full_df = pd.concat(df_list, ignore_index=True)

    # Prepare data
    full_df = prepare_stock_data(full_df)

    # Streamlit app launch (run: streamlit run your_script.py)
    streamlit_dashboard(full_df, sector_file)


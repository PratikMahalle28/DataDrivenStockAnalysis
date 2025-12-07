# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from ProjectTopicsWise.Streamlit.env.Scripts.analysis import load_stock_data, calculate_key_metrics, calculate_volatility, calculate_cumulative_returns
import sqlite3

st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")

@st.cache_data
def load_and_analyze_data():
    df = load_stock_data()
    green, red, summary, yearly_returns = calculate_key_metrics(df)
    volatility_df = calculate_volatility(df)
    cum_returns_df, top_5_stocks = calculate_cumulative_returns(df)
    return df, green, red, summary, yearly_returns, volatility_df, cum_returns_df, top_5_stocks

# Load data
df, green_stocks, red_stocks, market_summary, yearly_returns, volatility_df, cum_returns_df, top_5_stocks = load_and_analyze_data()

st.title("📈 Nifty 50 Stock Performance Dashboard")
st.markdown("---")

# Market Overview Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Green Stocks", f"{market_summary['green_stocks']}", delta=f"+{market_summary['green_stocks']}")
with col2:
    st.metric("Red Stocks", f"{market_summary['red_stocks']}", delta=f"+{market_summary['red_stocks']}")
with col3:
    st.metric("Avg Close Price", f"₹{market_summary['avg_close_price']:.2f}")
with col4:
    st.metric("Avg Volume", f"{market_summary['avg_volume']:,.0f}")

st.markdown("---")

# Top Performers Row
col1, col2 = st.columns(2)
with col1:
    st.subheader("🚀 Top 10 Green Stocks")
    st.dataframe(green_stocks.style.format({'Yearly_Return': '{:.2f}%'}).background_gradient())
with col2:
    st.subheader("📉 Top 10 Red Stocks")
    st.dataframe(red_stocks.style.format({'Yearly_Return': '{:.2f}%'}).background_gradient(cmap='Reds'))

# Volatility Chart
st.subheader("⚡ Top 10 Most Volatile Stocks")
fig_vol = px.bar(volatility_df.head(10), x='Symbol', y='Volatility', 
                 title="Annualized Volatility (Std Dev of Daily Returns)",
                 color='Volatility', color_continuous_scale='Reds')
st.plotly_chart(fig_vol, use_container_width=True)

# Cumulative Returns
st.subheader("📊 Cumulative Returns - Top 5 Stocks")
fig_cum = go.Figure()
for stock in top_5_stocks:
    fig_cum.add_trace(go.Scatter(x=cum_returns_df.index, y=cum_returns_df[stock],
                                mode='lines', name=stock))
fig_cum.update_layout(title="Cumulative Returns Over Time", xaxis_title="Date", yaxis_title="Cumulative Return")
st.plotly_chart(fig_cum, use_container_width=True)

# Correlation Heatmap
st.subheader("🔗 Stock Price Correlation Heatmap")
close_prices = df.pivot(index='Date', columns='Symbol', values='Close').dropna(axis=1)
corr_matrix = close_prices.corr()
fig_corr = px.imshow(corr_matrix, aspect="auto", color_continuous_scale='RdBu_r',
                    title="Correlation Between Stock Closing Prices")
st.plotly_chart(fig_corr, use_container_width=True)

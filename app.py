# app.py - ALL BAR CHARTS FIXED WITH PROPER % LABELS
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from analysis import (load_stock_data, calculate_key_metrics, 
                      calculate_volatility, calculate_cumulative_returns,
                      get_sector_performance, calculate_correlation,
                      get_monthly_top_gainers_losers)

# 🚨 MYSQL DATABASE CONNECTION
DB_CONFIG = {
    'user': 'root',
    'password': 'Pratik28@',
    'host': 'localhost',
    'port': '3306',
    'database': 'stock_analysis_db'
}

# Create connection string
encoded_password = quote_plus(DB_CONFIG['password'])
connection_string = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{encoded_password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string, pool_pre_ping=True)

st.set_page_config(page_title="Stock Performance Dashboard", layout="wide")

@st.cache_data
def load_and_analyze():
    """Load data from CSV and analyze - FULLY INTEGRATED WITH ALL REQUIREMENTS"""
    try:
        print("🔄 Loading data...")
        df = load_stock_data()
        print(f"📊 Raw data shape: {df.shape}")
        
        if df.empty:
            st.warning("❌ No data found in 'data/csv/' folder")
            return pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
        
        print(f"📊 Analyzing {len(df)} rows from {df['Symbol'].nunique()} stocks...")
        
        top_green, top_red, market_summary, yearly_returns = calculate_key_metrics(df)
        volatility = calculate_volatility(df)
        cum_returns_data, top_stocks = calculate_cumulative_returns(df)
        sector_perf = get_sector_performance(df)
        correlation = calculate_correlation(df)
        monthly_analysis = get_monthly_top_gainers_losers(df, top_n=5)
        
        print(f"✅ Metrics calculated: {len(top_green)} green, {len(top_red)} red stocks")
        print(f"📈 Volatility shape: {volatility.shape}")
        print(f"📊 Cum returns shape: {cum_returns_data.shape}")
        print(f"🏭 Sector perf: {len(sector_perf)} sectors")
        print(f"🔗 Correlation: {correlation.shape}")
        print(f"📅 Monthly: {len(monthly_analysis)} months")
        
        metrics = {
            'top_green': top_green,
            'top_red': top_red,
            'market_summary': market_summary,
            'sector_perf': sector_perf,
            'correlation': correlation,
            'volatility': volatility,
            'cum_returns': cum_returns_data,
            'monthly_analysis': monthly_analysis
        }
        
        try:
            df.to_sql('raw_stock_data', engine, if_exists='replace', index=False)
            print("✅ Data saved to MySQL!")
        except Exception as db_error:
            print(f"⚠️ MySQL save failed: {db_error}")
        
        return df, metrics, volatility, cum_returns_data, sector_perf, correlation, pd.DataFrame(), monthly_analysis
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in load_and_analyze: {e}")
        st.error(f"❌ Error: {e}")
        return pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}

# Initialize session state
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False

@st.cache_resource
def test_db_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            st.session_state.db_connected = True
            return "✅ Database Ready"
    except Exception as e:
        st.session_state.db_connected = False
        print(f"❌ DB Connection error: {e}")
        return "❌ Database Error"

# Load data
print("🚀 Starting main app load...")
df, metrics, volatility, cum_returns, sector_perf_df, correlation, unused, monthly_analysis = load_and_analyze()
print("✅ Main data load complete!")

# 5-TAB DASHBOARD
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "🔍 Filters & Charts", "🏭 Sectors", "🔗 Advanced", "📅 Monthly"])

with tab1:
    st.sidebar.title("🗄️ Status")
    db_status = test_db_connection()
    st.sidebar.info(db_status)
    
    if st.sidebar.checkbox("🔍 Debug Mode"):
        st.sidebar.write("**Metrics keys:**", list(metrics.keys()))
        st.sidebar.write("**Data shape:**", df.shape if not df.empty else "No data")
    
    st.title("📈 Nifty 50 Stock Performance Dashboard")
    st.markdown("**✅ ALL 5 REQUIREMENTS IMPLEMENTED**")
    st.markdown("---")
    
    # MARKET SUMMARY CARDS
    col1, col2, col3, col4, col5 = st.columns(5)
    market_summary = metrics.get('market_summary', {})
    
    with col1:
        st.metric("Total Stocks", market_summary.get('total_stocks', 0))
    with col2:
        st.metric("Green Stocks", market_summary.get('green_stocks', 0))
    with col3:
        st.metric("Avg Close", f"₹{market_summary.get('avg_close_price', 0):,.0f}")
    with col4:
        st.metric("Avg Volume", f"{market_summary.get('avg_volume', 0):,.0f}")
    with col5:
        total = market_summary.get('total_stocks', 1)
        green_pct = market_summary.get('green_stocks', 0) / total * 100
        st.metric("Green %", f"{green_pct:.1f}%")
    
    # TOP 10 GREEN/RED STOCKS
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Top 10 Green Stocks")
        top_green = metrics.get('top_green', pd.DataFrame())
        if not top_green.empty:
            top_green_display = top_green.copy()
            top_green_display['Yearly_Return_%'] = top_green_display['Yearly_Return'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(top_green_display[['Symbol', 'Yearly_Return_%']], use_container_width=True)
    
    with col2:
        st.subheader("📉 Top 10 Red Stocks")
        top_red = metrics.get('top_red', pd.DataFrame())
        if not top_red.empty:
            top_red_display = top_red.copy()
            top_red_display['Yearly_Return_%'] = top_red_display['Yearly_Return'].apply(lambda x: f"{x:.2f}%")
            st.dataframe(top_red_display[['Symbol', 'Yearly_Return_%']], use_container_width=True)

with tab2:
    st.subheader("🔍 **Interactive Controls**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        all_stocks = sorted(df['Symbol'].unique()) if not df.empty else []
        selected_stocks = st.multiselect(
            "Select Stocks", 
            options=all_stocks,
            default=all_stocks[:5] if len(all_stocks) > 0 else [],
            max_selections=10
        )
    
    with col2:
        top_n = st.slider("Top N Stocks", 5, 20, 10)
    
    with col3:
        chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Area"])
    
    # ✅ FIXED VOLATILITY CHART - PROPER % LABELS
    st.subheader("⚡ Top 10 Most Volatile Stocks")
    if not volatility.empty:
        top_10_vol = volatility.head(10)
        fig_vol = px.bar(top_10_vol, 
                        x='Symbol', 
                        y='Volatility',
                        title="Top 10 Most Volatile Stocks (Annualized Std Dev %)",
                        color='Volatility', 
                        color_continuous_scale='Reds',
                        text='Volatility')  # ✅ FIXED: Added text='Volatility'
        
        fig_vol.update_traces(
            texttemplate='%{text:.1f}%',  # ✅ FIXED: Clean % label
            textposition='outside',
            textfont_size=12
        )
        fig_vol.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig_vol, use_container_width=True)
    
    # CUMULATIVE RETURNS (Line chart - no bar labels needed)
    st.subheader("📈 Cumulative Returns - Top 5 Performing Stocks")
    if not cum_returns.empty:
        fig_cumulative = px.line(cum_returns, 
                               x=cum_returns.index, 
                               y=cum_returns.columns,
                               title="Cumulative Returns: Top 5 Performing Stocks",
                               labels={'value': 'Cumulative Return (%)', 'variable': 'Stock'})
        fig_cumulative.update_layout(height=500)
        st.plotly_chart(fig_cumulative, use_container_width=True)
    
    # Interactive Stock Comparison
    st.subheader("📊 Interactive Stock Comparison")
    if not df.empty and selected_stocks:
        filtered_df = df[df['Symbol'].isin(selected_stocks)]
        if chart_type == "Line":
            fig_compare = px.line(filtered_df, x='Date', y='Close', color='Symbol',
                                title=f"Price Evolution - {len(selected_stocks)} Stocks")
        elif chart_type == "Area":
            fig_compare = px.area(filtered_df, x='Date', y='Close', color='Symbol')
        else:
            fig_compare = px.bar(filtered_df.groupby(['Symbol', 'Date'])['Close'].mean().reset_index(),
                               x='Date', y='Close', color='Symbol')
        fig_compare.update_layout(height=500)
        st.plotly_chart(fig_compare, use_container_width=True)

# ✅ FIXED TAB3 - PERFECT SECTOR CHART
with tab3:
    st.subheader("🏭 Sector-wise Performance Analysis")
    
    sector_perf = metrics.get('sector_perf', pd.DataFrame())
    if not sector_perf.empty:
        # ✅ FIXED: Perfect sector bar chart
        fig_sector = px.bar(sector_perf, 
                          x='Sector', 
                          y='Return',
                          title="Average Yearly Return by Sector (%)",
                          color='Return',
                          color_continuous_scale=['red', 'yellow', 'green'],
                          text='Return')  # ✅ CRITICAL: text='Return'
        
        fig_sector.update_traces(
            texttemplate='%{text:.1f}%',  # ✅ FIXED: Simple clean % label
            textposition='outside',
            textfont_size=12
        )
        
        fig_sector.update_layout(
            height=500,
            xaxis_tickangle=-45,
            yaxis_title="Yearly Return (%)",
            showlegend=False
        )
        st.plotly_chart(fig_sector, use_container_width=True)
        
        # Enhanced table
        st.subheader("📋 Sector Performance Details")
        display_table = sector_perf[['Sector', 'Return']].copy()
        display_table['Return (%)'] = display_table['Return'].apply(lambda x: f"{x:.2f}%")
        st.dataframe(display_table.sort_values('Return', ascending=False), use_container_width=True)
    else:
        st.info("📊 Create **data/sectors.csv** with **Symbol,Sector** columns")
        st.code("Symbol,Sector\nRELIANCE,Energy\nTCS,IT\nHDFCBANK,Financials")

with tab4:
    st.subheader("🔗 Stock Price Correlation Matrix")
    
    correlation_matrix = metrics.get('correlation', pd.DataFrame())
    if not correlation_matrix.empty:
        n_stocks = st.slider("Matrix Size", 6, 15, 12)
        corr_subset = correlation_matrix.iloc[:n_stocks, :n_stocks]
        
        fig_corr = px.imshow(corr_subset,
                           title=f"Stock Price Correlation Heatmap ({n_stocks}x{n_stocks})",
                           color_continuous_scale='RdBu_r',
                           color_continuous_midpoint=0)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        corr_values = corr_subset.values[np.triu_indices_from(corr_subset.values, k=1)]
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Avg Correlation", f"{corr_values.mean():.3f}")
        with col2: st.metric("Highest Correlation", f"{corr_values.max():.3f}")
        with col3: st.metric("Lowest Correlation", f"{corr_values.min():.3f}")
    
    st.subheader("📋 Raw Data Explorer")
    if not df.empty:
        st.dataframe(df, use_container_width=True)

with tab5:
    st.subheader("📅 Monthly Top 5 Gainers & Losers")
    
    monthly_analysis = metrics.get('monthly_analysis', {})
    if monthly_analysis:
        months = sorted(monthly_analysis.keys(), reverse=True)
        selected_month = st.selectbox("📋 Select Month", months)
        
        month_data = monthly_analysis[selected_month]
        gainers = month_data['gainers']
        losers = month_data['losers']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🚀 Top 5 Gainers - {selected_month}")
            if not gainers.empty:
                gainers_display = gainers.copy()
                gainers_display['Return_%'] = gainers_display['Monthly_Return'].apply(lambda x: f"{x:.2f}%")
                st.dataframe(gainers_display[['Symbol', 'Return_%']], use_container_width=True)
        
        with col2:
            st.subheader(f"📉 Top 5 Losers - {selected_month}")
            if not losers.empty:
                losers_display = losers.copy()
                losers_display['Return_%'] = losers_display['Monthly_Return'].apply(lambda x: f"{x:.2f}%")
                st.dataframe(losers_display[['Symbol', 'Return_%']], use_container_width=True)
        
        # ✅ FIXED MONTHLY TREND CHART
        st.subheader("📊 Top Gainers Trend Across All Months")
        all_gainers = pd.concat([data['gainers'] for data in monthly_analysis.values()])
        if not all_gainers.empty:
            top_gainers_monthly = all_gainers.nlargest(10, 'Monthly_Return')
            fig_monthly = px.bar(top_gainers_monthly, 
                               x='Symbol', 
                               y='Monthly_Return',
                               title="Top Monthly Gainers Across All Months",
                               color='Monthly_Return',
                               text='Monthly_Return')  # ✅ FIXED
            fig_monthly.update_traces(
                texttemplate='%{text:.1f}%',  # ✅ FIXED
                textposition='outside'
            )
            st.plotly_chart(fig_monthly, use_container_width=True)

st.markdown("---")
st.markdown("**✅ ALL BAR CHARTS FIXED**")
st.caption("🚀 Stock Analysis Dashboard")

# %% [markdown]
# # 🌌 CRYPTOSTOCK-ORACLE: Day 2 Interactive Terminal Integration
# ---
# This module integrates the interactive tracking infrastructure, multi-axis plotly subplots, 
# and structural layout configurations for both Equities and Decentralized crypto nodes.

# %%
# [Include imports and Day 1 code blocks here]
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app_day1 import fetch_market_matrix

# Extend Sidebar Configuration Panel
page_selection = st.sidebar.radio("🧭 Navigation Matrix Panel", ["📃 1. Project Manifesto & Core Rationale", "📊 2. Real-Time Microstructure Terminal"])

if page_selection == "📊 2. Real-Time Microstructure Terminal":
    st.markdown("<h1 class='glow-text'>⚡ Real-Time Multi-Asset Analysis Engine</h1>", unsafe_allow_html=True)
    market_tab, crypto_tab = st.tabs(["🏛️ Traditional Equity Indexes", "⚡ Decentralized Digital Assets"])
    
    with market_tab:
        equity_ticker = st.selectbox("🎯 Target Corporate Equity Asset", ["AAPL", "MSFT", "NVDA"])
        user_lookback = st.slider("📆 Lookback Window (days)", min_value=10, max_value=120, value=30, step=1)
        eq_data = fetch_market_matrix(equity_ticker, lookback_days=user_lookback)
        
        # Subplot Engine Logic
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                            subplot_titles=('1. Candlestick Matrix', '2. Trends', '3. RSI Space', '4. Liquidity Turnover'))
        fig.add_trace(go.Candlestick(x=eq_data.index, open=eq_data['Open'], high=eq_data['High'], low=eq_data['Low'], close=eq_data['Close']), row=1, col=1)
        fig.add_trace(go.Scatter(x=eq_data.index, y=eq_data['SMA_20'], line=dict(color='cyan')), row=2, col=1)
        fig.add_bar(x=eq_data.index, y=eq_data['Volume'], marker_color='cyan', name='Volume'), row=4, col=1
        fig.update_layout(height=900, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
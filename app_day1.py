# %% [markdown]
# # 🌌 CRYPTOSTOCK-ORACLE: Day 1 Framework Initialization
# ---
# This module implements the foundational layer of our custom glassmorphism platform, 
# global configuration states, and optimized caching engines for data ingestion.

# %%
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt

# ⚙️ SYSTEM HORIZON CONFIGURATION
st.set_page_config(
    page_title="Vortex.Quant Terminal",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🧪 GLASSMORPHISM LAYER INJECTION (CUSTOM CSS/HTML UI GLOW)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght=300;400;600&family=Space+Grotesk:wght=400;600&display=swap');
    .stApp { background: linear-gradient(135deg, #0b0f19 0%, #020408 100%) !important; font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(11, 15, 25, 0.7) !important; backdrop-filter: blur(12px) !important; border-right: 1px solid rgba(255, 255, 255, 0.05) !important; }
    .glass-card { background: rgba(255, 255, 255, 0.03) !important; backdrop-filter: blur(16px) !important; border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.07) !important; padding: 25px !important; margin-bottom: 25px !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important; transition: all 0.4s ease-in-out; }
    .glass-card:hover { border: 1px solid rgba(99, 102, 241, 0.3) !important; box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.1) !important; transform: translateY(-2px); }
    .glow-text { font-family: 'Space Grotesk', sans-serif; color: #ffffff; text-shadow: 0 0 10px rgba(99, 102, 241, 0.5); font-weight: 600; }
    .stButton>button { background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: 600 !important; transition: all 0.3s ease; }
    .stButton>button:hover { box-shadow: 0 0 15px rgba(168, 85, 247, 0.6) !important; transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# 📡 UTILITY COMPONENT: HIGH-SPEED PIPELINE ENGINE
@st.cache_data(ttl=3600)
def fetch_market_matrix(ticker, lookback_days=365):
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=lookback_days)
    raw = yf.download(ticker, start=start_date, end=end_date)
    df = pd.DataFrame(index=raw.index)
    df['Open'] = raw['Open'].values
    df['High'] = raw['High'].values
    df['Low'] = raw['Low'].values
    df['Close'] = raw['Close'].values
    df['Volume'] = raw['Volume'].values
    
    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    df['Std_20'] = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['SMA_20'] + (df['Std_20'] * 2)
    df['BB_Lower'] = df['SMA_20'] - (df['Std_20'] * 2)
    
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0.0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))
    return df.dropna()

# 🎛️ SIDEBAR CONTROL CONSOLE
st.sidebar.markdown("<h2 class='glow-text'>🌌 VORTEX.QUANT</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")
page_selection = st.sidebar.radio("🧭 Navigation Matrix Panel", ["📃 1. Project Manifesto & Core Rationale"])
st.sidebar.markdown("---")
user_lookback = st.sidebar.slider("📅 Data Horizon Lookback (Days)", 180, 1000, 500)

if page_selection == "📃 1. Project Manifesto & Core Rationale":
    st.markdown("<h1 class='glow-text'>🪐 Vortex.Quant Architectural Manifesto</h1>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'><h3>💎 1.1 Architectural Rationale</h3><p>Modern global financial markets operate via high-speed matching networks where pricing inefficiencies exist for mere milliseconds...</p></div>", unsafe_allow_html=True)
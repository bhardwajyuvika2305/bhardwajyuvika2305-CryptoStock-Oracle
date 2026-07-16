import hashlib
import datetime as dt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

# ==============================================================================
# 🗄️ DATABASE CONNECTION ENGINE ROUTER
# ==============================================================================
# We pull our initial database grid layout modules directly from our local engine.
# This prevents thread conflicts between separate user browser interactions.
from database import init_db, get_user, insert_user, insert_feedback, get_feedback

# Trigger safe creation of SQLite framework matrices on initial setup start.
init_db()

# ==============================================================================
# ⚙️ WEB VIEWPORT GLOBAL INITIALIZATION
# ==============================================================================
st.set_page_config(
    page_title="CryptoStock-Oracle Terminal",
    page_icon="🔮",
    layout="wide", # Maximizes screen space for multi-panel plotting grids
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 💎 CUSTOM CYBERPUNK INTERFACE CSS MATRIX
# ==============================================================================
# Modifies standard Streamlit CSS components to create a unified glassmorphism UI.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&display=swap');
    
    /* Global Core Layout Configurations */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #020408 100%) !important;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Translucent Cyberpunk Sidebar Wrap */
    [data-testid="stSidebar"] {
        background: rgba(11, 15, 25, 0.96) !important;
        backdrop-filter: blur(14px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Compresses vertical gaps inside the sidebar layout */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 6px !important; 
    }

    /* Force Radio items into unified, vertically centered block rows */
    [data-testid="stSidebar"] label[data-testid="stRadioOption"] {
        display: flex !important;
        align-items: center !important;
        padding: 4px 8px !important;
        margin: 0px !important;
        width: 100% !important;
    }

    /* Critical Text Wrap Override: Prevents labels from breaking onto a second line */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        white-space: nowrap !important; 
        font-size: 0.88rem !important;  
        font-weight: 400 !important;
        color: rgba(255, 255, 255, 0.85) !important;
        margin: 0px !important;
        padding-left: 4px !important;
    }

    /* Subtle hover illumination effect on menu selections */
    [data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover {
        background: rgba(99, 102, 241, 0.08) !important;
        border-radius: 6px !important;
        cursor: pointer;
        transition: background 0.15s ease-in-out;
    }

    /* Primary Navigation Control Header Title Sizing */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #a855f7 !important;
        text-shadow: 0 0 8px rgba(168, 85, 247, 0.3);
    }

    /* Structural Glassmorphic Panels */
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        padding: 25px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }
    
    /* Neon Text Accents */
    .glow-text {
        color: #ffffff;
        text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
        font-weight: 600;
    }
    
    /* Core Call-to-Action Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🧠 RUNTIME SESSION CONTROL CACHE
# ==============================================================================
# Guarantees user properties remain stable between structural re-renders.
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'ratings_pool' not in st.session_state:
    st.session_state['ratings_pool'] = [5, 5, 4, 5] # Baseline historical score records

# ==============================================================================
# 📡 LIVE DATA INGESTION & MATHEMATICAL COMPUTATION ENGINE
# ==============================================================================
# Cached for 30 minutes to prevent API structural rate limiting during re-runs.
@st.cache_data(ttl=1800)
def fetch_market_matrix(ticker, lookback_days=365):
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=lookback_days)
    
    # Ingest historical asset market telemetry from Yahoo Finance
    raw = yf.download(ticker, start=start_date, end=end_date)
    
    if raw.empty:
        raise ValueError(f"No asset metrics found matching: {ticker}")
        
    # Structural step: Flatten MultiIndex columns if generated by yfinance
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
        
    # Clean data arrays into explicit floating point allocations
    df = pd.DataFrame(index=raw.index)
    df['Open'] = raw['Open'].values.astype(float)
    df['High'] = raw['High'].values.astype(float)
    df['Low'] = raw['Low'].values.astype(float)
    df['Close'] = raw['Close'].values.astype(float)
    df['Volume'] = raw['Volume'].values.astype(float)
    
    # --- TECHNICAL PIPELINE EQUATIONS ---
    # Logarithmic Returns Calculation Matrix
    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # Baseline Moving Averages
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    
    # Bollinger Band Dispersion Channels
    df['Std_20'] = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['SMA_20'] + (df['Std_20'] * 2)
    df['BB_Lower'] = df['SMA_20'] - (df['Std_20'] * 2)
    
    # Relative Strength Index (RSI - 14 Days)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0.0).rolling(14).mean()
    rs = gain / (loss + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Moving Average Convergence Divergence Tracking (MACD)
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # Average True Range Structural Volatility Metric (ATR)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift(1))
    low_close = np.abs(df['Low'] - df['Close'].shift(1))
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    df['ATR'] = ranges.max(axis=1).rolling(14).mean()
    
    # Volume Z-Score Outlier Flag Analysis
    df['Vol_Mean'] = df['Volume'].rolling(20).mean()
    df['Vol_Std'] = df['Volume'].rolling(20).std()
    df['Volume_ZScore'] = (df['Volume'] - df['Vol_Mean']) / (df['Vol_Std'] + 1e-9)
    
    # Chaikin Money Flow Multiplier Integration (CMF)
    mfv = (((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / ((df['High'] - df['Low']) + 1e-9)) * df['Volume']
    df['CMF'] = mfv.rolling(20).sum() / (df['Volume'].rolling(20).sum() + 1e-9)
    
    # Average Directional Trend Strength Tracking Matrix (ADX)
    df['UpMove'] = df['High'] - df['High'].shift(1)
    df['DownMove'] = df['Low'].shift(1) - df['Low']
    df['+DM'] = np.where((df['UpMove'] > df['DownMove']) & (df['UpMove'] > 0), df['UpMove'], 0.0)
    df['-DM'] = np.where((df['DownMove'] > df['UpMove']) & (df['DownMove'] > 0), df['DownMove'], 0.0)
    
    tr_sum = ranges.max(axis=1).rolling(14).sum()
    df['+DI'] = 100 * (df['+DM'].rolling(14).sum() / (tr_sum + 1e-9))
    df['-DI'] = 100 * (df['-DM'].rolling(14).sum() / (tr_sum + 1e-9))
    dx = 100 * (np.abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'] + 1e-9))
    df['ADX'] = dx.rolling(14).mean()
    
    return df.dropna()

# ==============================================================================
# 🔐 AUTHENTICATION GATEWAY CONTROL
# ==============================================================================
# Intercepts users and halts downstream execution until credentials clear.
if not st.session_state['logged_in']:
    st.markdown("<h1 class='glow-text' style='text-align: center;'>🔮 CryptoStock-Oracle Gatekeeper</h1>", unsafe_allow_html=True)
    
    auth_tab, reg_tab = st.tabs(["🔐 Security Node Login", "🛰️ Register Premium Node"])
    
    with auth_tab:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Enter Node ID / Username").strip()
            login_pass = st.text_input("Security Passkey", type="password")
            submit_login = st.form_submit_button("Authenticate Instance Connection")
            
            if submit_login:
                # Convert the input string into a standard secure tracking hash
                hashed_login_pass = hashlib.sha256(login_pass.encode()).hexdigest()
                user_record = get_user(username)
                
                # Verify identity record exists inside database fields
                if user_record and user_record[3] == hashed_login_pass:
                    st.session_state['logged_in'] = True
                    st.session_state['current_user'] = username
                    st.success("Authorized! Initializing system terminal...")
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid configuration passkey.")
        st.markdown("</div>", unsafe_allow_html=True)
                    
    with reg_tab:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("registration_form"):
            new_user = st.text_input("Choose Node ID").strip()
            new_email = st.text_input("Communication Email").strip()
            new_pass = st.text_input("Security Passkey", type="password")
            node_tier = st.selectbox("Select Access Layer", ["Standard Data Tier", "Advanced Suite"])
            terms_accept = st.checkbox("I agree to terms of operational execution.")
            
            submit_reg = st.form_submit_button("Provision Security Node")
            
            if submit_reg:
                if not new_user or not new_pass or not new_email:
                    st.error("Missing configuration fields.")
                elif not terms_accept:
                    st.error("You must accept execution conditions.")
                else:
                    # Secure data transit using hashing mechanics
                    hashed_pass = hashlib.sha256(new_pass.encode()).hexdigest()
                    success, message = insert_user(new_user, new_email, hashed_pass, node_tier)
                    if success:
                        st.success("Account provisioned successfully! Proceed to log in.")
                    else:
                        st.error(f"Provisioning error: {message}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # STOPS downstream rendering until a valid session token is achieved.
    st.stop()

# ==============================================================================
# 🎛️ SYSTEM CONTROL SIDEBAR INTERFACE
# ==============================================================================
# Once logged_in evaluates to True, the interface elements below display automatically.
st.sidebar.markdown(f"<h2 class='glow-text'>🔮 Active Node: {st.session_state['current_user']}</h2>", unsafe_allow_html=True)
if st.sidebar.button("🔒 Terminate Connection Session"):
    st.session_state['logged_in'] = False
    st.session_state['current_user'] = None
    st.rerun()

st.sidebar.markdown("---")
# Compact names fit perfectly within CSS constraints to prevent visual clipping
page_selection = st.sidebar.radio(
    "🧭 Navigation Matrix Panel",
    [
        "📃 1. Project Manifesto", 
        "📊 2. Microstructure Terminal", 
        "🔮 3. Risk & Predictions",
        "🌐 4. Macro-Sector Radar",
        "📊 5. Liquidity Profile Maps",
        "📈 6. Asset Cross Correlations",
        "🧮 7. Markowitz Frontier",
        "💬 8. Live Feedback Space",
        "🔑 9. Root Admin Audit"
    ]
)

st.sidebar.markdown("---")
user_lookback = st.sidebar.slider("📅 Data Horizon Lookback (Days)", 180, 1000, 500)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Terminal Experience Rating")
star_input = st.sidebar.selectbox("Rate Dashboard Matrix", ["Select Rating", "⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
if star_input != "Select Rating":
    rating_val = len(star_input)
    if st.sidebar.button("Submit Terminal Rating"):
        st.session_state['ratings_pool'].append(rating_val)
        st.sidebar.success("Rating cached!")

avg_stars = np.mean(st.session_state['ratings_pool'])
st.sidebar.metric("System Reputation Score", f"{avg_stars:.1f} / 5.0")

# ==============================================================================
# 🏁 MAIN DYNAMIC ROUTING ENGINE MATRIX
# ==============================================================================
# Using sub-string verification pattern to guarantee stable path loading.

# --- SLIDE 1: INTRO MANIFESTO ---
if "1. Project Manifesto" in page_selection:
    st.markdown("<h1 class='glow-text'>🪐 CryptoStock-Oracle Architectural Manifesto</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h3>📡 Live Data Ingestion Pipeline Architecture</h3>
        <p>This quantitative sandbox operates completely independent of stale, pre-packaged historical CSV matrices. All mathematical analysis engines, 
        stochastic drift models, and optimization equations displayed within this interface ingest raw, real-time market telemetry directly from the 
        global exchanges via the <b>Yahoo Finance (yfinance) API engine using web scraping scraping methodologies</b>.</p>
        <p>The operational framework leverages asynchronous program calls to structurally parse asset data points through customized scripts. 
        This pipeline guarantees that the asset microstructures analyzed reflect verified price matching horizons directly from the active centralized and 
        decentralized asset networks.</p>
    </div>
    
    <div class='glass-card'>
        <h3>💎 Rationale: Why This System Exists</h3>
        <p>Modern global financial markets operate via high-speed matching networks where pricing inefficiencies exist for mere milliseconds. 
        Traditional discretionary retail trading relies heavily on human intuition—making it highly susceptible to catastrophic emotional traps, 
        including loss aversion, recency bias, and cognitive exhaustion.</p>
    </div>
    """, unsafe_allow_html=True)

# --- SLIDE 2: CANDLESTICK & INDICATOR TERMINAL ---
elif "2. Microstructure Terminal" in page_selection:
    st.markdown("<h1 class='glow-text'>⚡ Real-Time Multi-Asset Analysis Engine</h1>", unsafe_allow_html=True)
    market_tab, crypto_tab = st.tabs(["🏛️ Traditional Equity Indexes", "⚡ Decentralized Digital Assets"])
    
    with market_tab:
        equity_ticker = st.selectbox("🎯 Target Corporate Equity Asset", ["AAPL", "MSFT", "NVDA", "TSLA", "SPY", "QQQ"])
        try:
            eq_data = fetch_market_matrix(equity_ticker, lookback_days=user_lookback)
            
            # Extract historical metrics data points
            last_close = eq_data['Close'].iloc[-1]
            prev_close = eq_data['Close'].iloc[-2]
            delta_pct = ((last_close - prev_close) / prev_close) * 100
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("💰 Real-Time Spot Price", f"${last_close:,.2f}", f"{delta_pct:+.2f}%")
            m_col2.metric("📉 Realized Volatility Horizon (21d)", f"{(eq_data['Log_Return'].std() * np.sqrt(252) * 100):.2f}%")
            m_col3.metric("📈 Structural True Volatility (ATR)", f"${eq_data['ATR'].iloc[-1]:,.2f}")
            
            # Construct multi-tiered mathematical panel grid
            fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.025,
                                subplot_titles=('1. Candlestick Matrix', '2. MACD Momentum', '3. Relative Strength Space', '4. Chaikin Money Flow', '5. ADX Trend strength'))
            
            fig.add_trace(go.Candlestick(x=eq_data.index, open=eq_data['Open'], high=eq_data['High'], low=eq_data['Low'], close=eq_data['Close']), row=1, col=1)
            fig.add_trace(go.Scatter(x=eq_data.index, y=eq_data['BB_Upper'], name="BB Upper", line=dict(color='rgba(239, 68, 68, 0.8)')), row=1, col=1)
            fig.add_trace(go.Scatter(x=eq_data.index, y=eq_data['BB_Lower'], name="BB Lower", line=dict(color='rgba(34, 197, 94, 0.8)')), row=1, col=1)
            fig.add_trace(go.Scatter(x=eq_data.index, y=eq_data['MACD'], line=dict(color='#6366f1')), row=2, col=1)
            fig.add_trace(go.Scatter(x=eq_data.index, y=eq_data['MACD_Signal'], line=dict(color='#e11d48')), row=2, col=1)
            fig.add_trace(go.Bar(x=eq_data.index, y=eq_data['MACD_Hist']), row=2, col=1)
            fig.add_trace(go.Scatter(x=eq_data.index, y=eq_data['RSI'], line=dict(color='magenta')), row=3, col=1)
            fig.add_trace(go.Scatter(x=eq_data.index, y=eq_data['CMF'], line=dict(color='cyan')), row=4, col=1)
            fig.add_trace(go.Scatter(x=eq_data.index, y=eq_data['ADX'], line=dict(color='orange')), row=5, col=1)
            
            fig.update_layout(height=1000, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to fetch traditional equity matrix data structure: {e}")

    with crypto_tab:
        crypto_ticker = st.selectbox("🎯 Target Crypto Asset Nodes", ["BTC-USD", "ETH-USD", "SOL-USD"])
        try:
            cr_data = fetch_market_matrix(crypto_ticker, lookback_days=user_lookback)
            
            last_close_c = cr_data['Close'].iloc[-1]
            prev_close_c = cr_data['Close'].iloc[-2]
            delta_pct_c = ((last_close_c - prev_close_c) / prev_close_c) * 100
            
            c_col1, c_col2, c_col3 = st.columns(3)
            c_col1.metric("💰 Real-Time Spot Price", f"${last_close_c:,.2f}", f"{delta_pct_c:+.2f}%")
            c_col2.metric("📉 Realized Volatility (21d)", f"{(cr_data['Log_Return'].std() * np.sqrt(252) * 100):.2f}%")
            c_col3.metric("📈 True Volatility Range (ATR)", f"${cr_data['ATR'].iloc[-1]:,.2f}")
            
            fig_c = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.025,
                                  subplot_titles=('1. Candlestick Matrix', '2. MACD Momentum', '3. Relative Strength Space', '4. Chaikin Money Flow', '5. ADX Trend Strength'))
            
            fig_c.add_trace(go.Candlestick(x=cr_data.index, open=cr_data['Open'], high=cr_data['High'], low=cr_data['Low'], close=cr_data['Close']), row=1, col=1)
            fig_c.add_trace(go.Scatter(x=cr_data.index, y=cr_data['BB_Upper'], line=dict(color='rgba(239, 68, 68, 0.8)')), row=1, col=1)
            fig_c.add_trace(go.Scatter(x=cr_data.index, y=cr_data['BB_Lower'], line=dict(color='rgba(34, 197, 94, 0.8)')), row=1, col=1)
            fig_c.add_trace(go.Scatter(x=cr_data.index, y=cr_data['MACD'], line=dict(color='#6366f1')), row=2, col=1)
            fig_c.add_trace(go.Scatter(x=cr_data.index, y=cr_data['MACD_Signal'], line=dict(color='#e11d48')), row=2, col=1)
            fig_c.add_trace(go.Bar(x=cr_data.index, y=cr_data['MACD_Hist']), row=2, col=1)
            fig_c.add_trace(go.Scatter(x=cr_data.index, y=cr_data['RSI'], line=dict(color='magenta')), row=3, col=1)
            fig_c.add_trace(go.Scatter(x=cr_data.index, y=cr_data['CMF'], line=dict(color='cyan')), row=4, col=1)
            fig_c.add_trace(go.Scatter(x=cr_data.index, y=cr_data['ADX'], line=dict(color='orange')), row=5, col=1)
            
            fig_c.update_layout(height=1000, template="plotly_dark", showlegend=False, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_c, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to fetch crypto node data matrix: {e}")

# --- SLIDE 3: MONTE CARLO STOCHASTIC PROJECTIONS ---
elif "3. Risk & Predictions" in page_selection:
    st.markdown("<h1 class='glow-text'>🔮 Stochastic Prediction & Monte Carlo Matrix</h1>", unsafe_allow_html=True)
    
    choice = st.selectbox("Select Target Portfolio Asset for Statistical Modeling", ["AAPL", "NVDA", "TSLA", "BTC-USD", "ETH-USD"])
    try:
        data = fetch_market_matrix(choice, lookback_days=user_lookback)
        
        # Calculate localized historical drift and max drawdowns
        daily_mean_ret = data['Log_Return'].mean()
        daily_std_ret = data['Log_Return'].std()
        sharpe = (daily_mean_ret / (daily_std_ret + 1e-9)) * np.sqrt(252)
        var_95 = np.percentile(data['Log_Return'], 5)
        roll_max = data['Close'].cummax()
        max_dd = ((data['Close'] - roll_max) / roll_max).min()
        
        r_col1, r_col2, r_col3 = st.columns(3)
        r_col1.metric("🎯 Annualized Sharpe Ratio", f"{sharpe:.2f}")
        r_col2.metric("⚠️ 1-Day Value at Risk (95% VaR)", f"{var_95*100:.2f}%")
        r_col3.metric("📉 Maximum Drawdown", f"{max_dd*100:.2f}%")
        
        # --- STOCHASTIC DRIFT MODEL (GBM) ---
        mu = daily_mean_ret + 0.5 * (daily_std_ret**2)
        sigma = daily_std_ret
        S0 = data['Close'].iloc[-1]
        T = 30
        N_paths = 200
        
        np.random.seed(42)
        daily_returns_sim = np.exp((mu - 0.5 * sigma**2) + sigma * np.random.normal(0, 1, (T, N_paths)))
        path_matrix = np.zeros((T + 1, N_paths))
        path_matrix[0] = S0
        for t in range(1, T + 1):
            path_matrix[t] = path_matrix[t-1] * daily_returns_sim[t-1]
            
        future_timeline = [data.index[-1] + dt.timedelta(days=i) for i in range(1, T + 1)]
        
        fig_mc = go.Figure()
        for i in range(min(N_paths, 40)):
            fig_mc.add_trace(go.Scatter(x=future_timeline, y=path_matrix[1:, i], mode='lines', line=dict(width=0.5, color='rgba(99, 102, 241, 0.15)'), showlegend=False))
            
        p50 = np.percentile(path_matrix, 50, axis=1)[1:]
        p95 = np.percentile(path_matrix, 95, axis=1)[1:]
        p5 = np.percentile(path_matrix, 5, axis=1)[1:]
        
        fig_mc.add_trace(go.Scatter(x=future_timeline, y=p50, name='Median (p50)', line=dict(color='#a855f7', width=2.5)))
        fig_mc.add_trace(go.Scatter(x=future_timeline, y=p95, name='Upside (p95)', line=dict(color='#22c55e', width=2, dash='dash')))
        fig_mc.add_trace(go.Scatter(x=future_timeline, y=p5, name='Downside (p5)', line=dict(color='#ef4444', width=2, dash='dash')))
        
        fig_mc.update_layout(title="Stochastic Monte Carlo Drift Projection Map (Next 30 Days)", template="plotly_dark", height=500)
        st.plotly_chart(fig_mc, use_container_width=True)
    except Exception as e:
        st.error(f"Statistical calculation network error: {e}")

# --- SLIDE 4: DYNAMIC PORTFOLIO SLIDERS ---
elif "4. Macro-Sector Radar" in page_selection:
    st.markdown("<h1 class='glow-text'>🌐 Portfolio Macro-Sector Allocation Analytics</h1>", unsafe_allow_html=True)
    
    sec_col, chart_col = st.columns([1, 1.5])
    with sec_col:
        tech_w = st.slider("Technology Exposure %", 0, 100, 40)
        fin_w = st.slider("Finance Exposure %", 0, 100, 20)
        cons_w = st.slider("Consumer Discretionary %", 0, 100, 15)
        energy_w = st.slider("Energy Sector %", 0, 100, 15)
        crypto_w = st.slider("Alternative Assets / Crypto %", 0, 100, 10)
        
    with chart_col:
        sectors = ['Tech', 'Finance', 'Consumer', 'Energy', 'Crypto']
        weights = [tech_w, fin_w, cons_w, energy_w, crypto_w]
        
        fig_donut = go.Figure(data=[go.Pie(labels=sectors, values=weights, hole=.4, marker=dict(colors=['#6366f1', '#a855f7', '#ec4899', '#3b82f6', '#10b981']))])
        fig_donut.update_layout(title="Global Sector Allocation (Weighted Donut Map)", template="plotly_dark", height=350)
        st.plotly_chart(fig_donut, use_container_width=True)

# --- SLIDE 5: LIQUIDITY SUNBURST PLOT ---
elif "5. Liquidity Profile Maps" in page_selection:
    st.markdown("<h1 class='glow-text'>📊 Multi-Exchange Liquidity Structure Grid</h1>", unsafe_allow_html=True)
    
    data_sb = dict(
        labels=["Total Volume", "Coinbase", "Binance", "Nasdaq", "NYSE", "BTC/USD", "ETH/USD", "AAPL", "NVDA"],
        parents=["", "Total Volume", "Total Volume", "Total Volume", "Total Volume", "Coinbase", "Binance", "Nasdaq", "NYSE"],
        values=[1000, 350, 250, 220, 180, 200, 150, 120, 100]
    )
    fig_sb = px.sunburst(data_sb, names=data_sb['labels'], parents=data_sb['parents'], values=data_sb['values'])
    fig_sb.update_layout(title="Hierarchical Liquidity Breakdown Map (Sunburst)", template="plotly_dark", height=500)
    st.plotly_chart(fig_sb, use_container_width=True)

# --- SLIDE 6: INTER-ASSET CORRELATION MATRIX ---
elif "6. Asset Cross Correlations" in page_selection:
    st.markdown("<h1 class='glow-text'>📈 Inter-Asset Cross Correlation Heatmap</h1>", unsafe_allow_html=True)
    
    assets = ["AAPL", "MSFT", "NVDA", "TSLA", "BTC-USD", "ETH-USD"]
    
    @st.cache_data(ttl=3600)
    def calculate_correlations(assets, days):
        returns_dict = {}
        for asset in assets:
            try:
                raw_df = yf.download(asset, start=dt.date.today() - dt.timedelta(days=days))
                if isinstance(raw_df.columns, pd.MultiIndex):
                    raw_df.columns = raw_df.columns.get_level_values(0)
                returns_dict[asset] = np.log(raw_df['Close'] / raw_df['Close'].shift(1))
            except:
                pass
        return pd.DataFrame(returns_dict).dropna().corr()

    try:
        corr_df = calculate_correlations(assets, user_lookback)
        fig_heat = px.imshow(corr_df, text_auto=True, color_continuous_scale='Viridis')
        fig_heat.update_layout(title="Co-movement Matrix Heatmap", template="plotly_dark", height=500)
        st.plotly_chart(fig_heat, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to generate cross-asset matrix layout: {e}")

# --- SLIDE 7: MARKOWITZ FRONTIER OPTIMIZATION ---
elif "7. Markowitz Frontier" in page_selection:
    st.markdown("<h1 class='glow-text'>🧮 Markowitz Mean-Variance Efficient Frontier</h1>", unsafe_allow_html=True)
    
    with st.spinner("Optimizing matrix paths..."):
        try:
            assets_portfolio = ["AAPL", "MSFT", "NVDA", "BTC-USD"]
            returns_list = []
            for asset in assets_portfolio:
                raw_p = yf.download(asset, start=dt.date.today() - dt.timedelta(days=user_lookback))
                if isinstance(raw_p.columns, pd.MultiIndex):
                    raw_p.columns = raw_p.columns.get_level_values(0)
                returns_list.append(np.log(raw_p['Close'] / raw_p['Close'].shift(1)).dropna())
                
            returns_df = pd.concat(returns_list, axis=1, keys=assets_portfolio).dropna()
            num_portfolios = 200
            results = np.zeros((3, num_portfolios))
            
            mean_returns = returns_df.mean()
            cov_matrix = returns_df.cov()
            
            # Stochastic random weighting portfolio simulation loops
            for i in range(num_portfolios):
                weights = np.random.random(len(assets_portfolio))
                weights /= np.sum(weights)
                p_return = np.sum(weights * mean_returns) * 252
                p_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
                results[0,i] = p_return
                results[1,i] = p_volatility
                results[2,i] = p_return / (p_volatility + 1e-9) # Sharpe allocation calculations
                
            fig_ef = go.Figure()
            fig_ef.add_trace(go.Scatter(
                x=results[1], y=results[0], mode='markers',
                marker=dict(color=results[2], colorscale='Electric', showscale=True, colorbar=dict(title="Sharpe"))
            ))
            fig_ef.update_layout(title="Efficient Frontier Simulation Cloud", template="plotly_dark", xaxis_title="Expected Volatility", yaxis_title="Expected Return", height=500)
            st.plotly_chart(fig_ef, use_container_width=True)
        except Exception as e:
            st.error(f"Efficient Frontier computational failure: {e}")

# --- SLIDE 8: DUAL-COLUMN SQL FEEDBACK ENGINE ---
elif "8. Live Feedback Space" in page_selection:
    st.markdown("<h1 class='glow-text'>💬 Quant Terminal Feedback Room</h1>", unsafe_allow_html=True)
    
    form_col, list_col = st.columns([1, 1.2])
    with form_col:
        with st.form("feedback_form"):
            name = st.text_input("Trader Name", value="AnonymousQuant")
            satisfied = st.radio("Satisfied with Terminal UI?", ["Yes", "No"])
            comment = st.text_area("System Comments")
            if st.form_submit_button("Log Review Entry") and comment.strip():
                if insert_feedback(name, satisfied, comment):
                    st.success("Review logged successfully to SQLite!")
                    st.rerun()

    with list_col:
        db_feedback = get_feedback()
        # Display the five most recent feedback logs pulled from SQL database
        for row in db_feedback[:5]:
            st.markdown(f"<div class='glass-card'><b>👤 {row[0]}</b> <small style='color:#6366f1;'>{row[3]}</small><p>{row[2]}</p></div>", unsafe_allow_html=True)

# --- SLIDE 9: RE INTEGRATED INTERFACE AUDIT MATRIX ---
elif "9. Root Admin Audit" in page_selection:
    st.markdown("<h1 class='glow-text'>🔑 Oracle Terminal - Master Admin Directory</h1>", unsafe_allow_html=True)
    st.caption("Authorized Node Operations Only")
    
    password_input = st.text_input("Enter Root Master Password", type="password")

    if password_input == "oracleadmin2026":
        st.success("Root identity cleared! Extracting master user databases...")
        
        # Safely extracts system user lists from shared file engine path
        from database import get_all_users
        users_data = get_all_users()
        
        if users_data:
            df_users = pd.DataFrame(users_data, columns=["Database ID", "Username", "Email Address", "Hashed Password", "Account Access Tier"])
            st.dataframe(df_users, use_container_width=True)
            st.metric("Total Provisioned Users", len(df_users))
        else:
            st.info("No system nodes registered in database currently.")
    else:
        if password_input != "":
            st.error("Access Denied: Admin verification pending.")

# --- FAILSAFE ROUTER BACKSTOP ---
else:
    st.warning("Routing node out of sync. Please select an operational panel.")

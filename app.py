# ==============================================================================
# 🌌 CRYPTOSTOCK-ORACLE : NEXT-GENERATION MULTI-REGIME QUANTITATIVE WEB PLATFORM
# ==============================================================================

import hashlib
import datetime as dt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

# 🗄️ LINK DIRECTLY TO YOUR NEW DATABASE ENGINE
from database import init_db, get_user, insert_user, insert_feedback, get_feedback

# Initialize SQL tables on launch
init_db()

# ==============================================================================
# ⚙️ SYSTEM HORIZON CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="CryptoStock-Oracle Terminal",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🧪 GLASSMORPHISM LAYER INJECTION (CUSTOM CSS/HTML UI GLOW)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&display=swap');
    
    /* 🪐 Global Application Body & Font Architecture */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #020408 100%) !important;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* 🧭 Sidebar Core Glassmorphism Layout */
    [data-testid="stSidebar"] {
        background: rgba(11, 15, 25, 0.96) !important;
        backdrop-filter: blur(14px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* 🎯 CRITICAL FIX: Sidebar Radio Layout Constraint Override */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 6px !important; /* Tightens vertical spacing so option 9 doesn't clip off-screen */
    }

    /* Force Radio Choices to stay flat and inline without breaking selection alignment */
    [data-testid="stSidebar"] label[data-testid="stRadioOption"] {
        display: flex !important;
        align-items: center !important;
        padding: 4px 8px !important;
        margin: 0px !important;
        width: 100% !important;
    }

    /* Fix radio button text layout engine */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        white-space: nowrap !important; /* Completely blocks text from jumping to a second line */
        font-size: 0.88rem !important;  /* Slightly condensed for optimal UI density */
        font-weight: 400 !important;
        color: rgba(255, 255, 255, 0.85) !important;
        margin: 0px !important;
        padding-left: 4px !important;
    }

    /* Smooth Cyberpunk Hover Interaction */
    [data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover {
        background: rgba(99, 102, 241, 0.08) !important;
        border-radius: 6px !important;
        cursor: pointer;
        transition: background 0.15s ease-in-out;
    }

    /* Fix Nav Matrix Header styling */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #a855f7 !important;
        text-shadow: 0 0 8px rgba(168, 85, 247, 0.3);
    }

    /* 💎 Glassmorphic Component Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        padding: 25px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }
    
    .glow-text {
        color: #ffffff;
        text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
        font-weight: 600;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        width: 100%;
        transition: transform 0.1s ease;
    }

    .stButton>button:active {
        transform: scale(0.98);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Essential Session State Parameters
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'equity_ticker' not in st.session_state:
    st.session_state['equity_ticker'] = "AAPL"
if 'crypto_ticker' not in st.session_state:
    st.session_state['crypto_ticker'] = "BTC-USD"
if 'ratings_pool' not in st.session_state:
    st.session_state['ratings_pool'] = [5, 5, 4, 5, 5]

# 📡 UTILITY COMPONENT: HIGH-SPEED PIPELINE ENGINE
@st.cache_data(ttl=1800)
def fetch_market_matrix(ticker, lookback_days=365):
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=lookback_days)
    raw = yf.download(ticker, start=start_date, end=end_date)
    
    if raw.empty:
        raise ValueError(f"No data returned for ticker {ticker}")
        
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
        
    df = pd.DataFrame(index=raw.index)
    df['Open'] = raw['Open'].values.astype(float)
    df['High'] = raw['High'].values.astype(float)
    df['Low'] = raw['Low'].values.astype(float)
    df['Close'] = raw['Close'].values.astype(float)
    df['Volume'] = raw['Volume'].values.astype(float)
    
    # Technical Calculations
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
    
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift(1))
    low_close = np.abs(df['Low'] - df['Close'].shift(1))
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    df['ATR'] = ranges.max(axis=1).rolling(14).mean()
    
    df['Vol_Mean'] = df['Volume'].rolling(20).mean()
    df['Vol_Std'] = df['Volume'].rolling(20).std()
    df['Volume_ZScore'] = (df['Volume'] - df['Vol_Mean']) / (df['Vol_Std'] + 1e-9)
    
    mfv = (((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / ((df['High'] - df['Low']) + 1e-9)) * df['Volume']
    df['CMF'] = mfv.rolling(20).sum() / (df['Volume'].rolling(20).sum() + 1e-9)
    
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
# 🔐 AUTHENTICATION GATE (SESSIONS LOCK DOWN)
# ==============================================================================
if not st.session_state['logged_in']:
    st.markdown("<h1 class='glow-text' style='text-align: center;'>🔮 CryptoStock-Oracle Gatekeeper</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a855f7;'>Access Restricted. Please log in or register your local security node.</p>", unsafe_allow_html=True)
    
    auth_tab, reg_tab = st.tabs(["🔐 Security Node Login", "🛰️ Register Premium Node"])
    
    with auth_tab:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Enter Node ID / Username").strip()
            login_pass = st.text_input("Security Passkey / Password", type="password")
            submit_login = st.form_submit_button("Authenticate Instance Connection")
            
            if submit_login:
                hashed_login_pass = hashlib.sha256(login_pass.encode()).hexdigest()
                # Use DB verify user
                user_record = get_user(username)
                if user_record and user_record[3] == hashed_login_pass:
                    st.session_state['logged_in'] = True
                    st.session_state['current_user'] = username
                    st.success(f"Security node authorized. Initializing connection...")
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid credentials.")
        st.markdown("</div>", unsafe_allow_html=True)
                    
    with reg_tab:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("registration_form"):
            new_user = st.text_input("Choose Node ID / Username").strip()
            new_email = st.text_input("Communication Email Address").strip()
            new_pass = st.text_input("Security Passkey / Password", type="password")
            node_tier = st.selectbox("Select Access Layer", ["Standard Data Tier", "Advanced Suite"])
            terms_accept = st.checkbox("I agree to terms of real-time sandbox rules.")
            
            submit_reg = st.form_submit_button("Provision Security Node")
            
            if submit_reg:
                if not new_user or not new_pass or not new_email:
                    st.error("Missing configuration fields.")
                elif not terms_accept:
                    st.error("You must accept execution conditions.")
                else:
                    hashed_pass = hashlib.sha256(new_pass.encode()).hexdigest()
                    success, message = insert_user(new_user, new_email, hashed_pass, node_tier)
                    if success:
                        st.success("Account created successfully! Proceed to log in.")
                    else:
                        st.error(f"Provisioning error: {message}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ==============================================================================
# 🎛️ SIDEBAR CONTROL CONSOLE (AUTHENTICATED)
# ==============================================================================
st.sidebar.markdown(f"<h2 class='glow-text'>🔮 Active Node: {st.session_state['current_user']}</h2>", unsafe_allow_html=True)
if st.sidebar.button("🔒 Terminate Connection Session"):
    st.session_state['logged_in'] = False
    st.session_state['current_user'] = None
    st.rerun()

st.sidebar.markdown("---")
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
        "🔑 9. Root Admin Audit"  # Compact name ensures it fits on screen!
    ]
)

st.sidebar.markdown("---")
user_lookback = st.sidebar.slider("📅 Data Horizon Lookback (Days)", 180, 1000, 500)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Terminal Experience Rating")
star_input = st.sidebar.selectbox("Rate our Quantitative Dashboard", ["Select Rating", "⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
if star_input != "Select Rating":
    rating_val = len(star_input)
    if st.sidebar.button("Submit Terminal Rating"):
        st.session_state['ratings_pool'].append(rating_val)
        st.sidebar.success("Rating cached!")

avg_stars = np.mean(st.session_state['ratings_pool'])
st.sidebar.metric("System Reputation Score", f"{avg_stars:.1f} / 5.0")


# ==============================================================================
# PAGE 1: PROJECT MANIFESTO & RATIONALE
# ==============================================================================
if page_selection == "📃 1. Project Manifesto & Core Rationale":
    st.markdown("<h1 class='glow-text'>🪐 CryptoStock-Oracle Architectural Manifesto</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-card'>
        <h3>💎 1.1 Architectural Rationale: Why This System Exists</h3>
        <p>Modern global financial markets operate via high-speed matching networks where pricing inefficiencies exist for mere milliseconds. 
        Traditional discretionary retail trading relies heavily on human intuition—making it highly susceptible to catastrophic emotional traps, 
        including loss aversion, recency bias, and cognitive exhaustion.</p>
    </div>
    """, unsafe_allow_html=True)
    
    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown("""
        <div class='glass-card'>
            <h3>🎯 1.2 Underlying Topic Selection</h3>
            <p>Our research focuses heavily on tracking the behavioral gaps between <b>Centralized Equity Auctions</b> and 
            <b>Decentralized Continuous Liquidity Networks</b>.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with right_col:
        st.markdown("""
        <div class='glass-card'>
            <h3>🚀 1.3 Future Operational Scope</h3>
            <p>The foundational layout of this sandbox allows it to scale directly into institutional trading spaces. By avoiding black-box AI dependencies, 
            the entire platform remains completely transparent.</p>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 2: REAL-TIME MICROSTRUCTURE TERMINAL
# ==============================================================================
elif page_selection == "📊 2. Real-Time Microstructure Terminal":
    st.markdown("<h1 class='glow-text'>⚡ Real-Time Multi-Asset Analysis Engine</h1>", unsafe_allow_html=True)
    market_tab, crypto_tab = st.tabs(["🏛️ Traditional Equity Indexes", "⚡ Decentralized Digital Assets"])
    
    with market_tab:
        equity_ticker = st.selectbox("🎯 Target Corporate Equity Asset", ["AAPL", "MSFT", "NVDA", "TSLA", "SPY", "QQQ"])
        st.session_state['equity_ticker'] = equity_ticker
        eq_data = fetch_market_matrix(equity_ticker, lookback_days=user_lookback)
        
        last_close = eq_data['Close'].iloc[-1]
        prev_close = eq_data['Close'].iloc[-2]
        delta_pct = ((last_close - prev_close) / prev_close) * 100
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("💰 Real-Time Spot Price", f"${last_close:,.2f}", f"{delta_pct:+.2f}%")
        m_col2.metric("📉 Realized Volatility Horizon (21d)", f"{(eq_data['Log_Return'].std() * np.sqrt(252) * 100):.2f}%")
        m_col3.metric("📈 Structural True Volatility (ATR)", f"${eq_data['ATR'].iloc[-1]:,.2f}")
        
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

        with st.expander("💡 New Trader Guide: How to Read This Big Technical Chart", expanded=False):
         st.markdown ("""
    This chart is broken into 5 layers to show you where the asset price is moving and whether people are buying or selling heavily right now.
    
    *   **1. The Candlestick Matrix (Top Chart)**: 
        *   *What it is:* Each bar represents one trading day. A **Green** bar means the price closed higher than it started; a **Red** bar means it dropped. 
        *   *The Outer Lines (Bollinger Bands):* Think of these as a rubber band cage. The price stays inside them 95% of the time. Right now, the safe floor is at **${eq_data['BB_Lower'].iloc[-1]:.2f}** and the ceiling is at **${eq_data['BB_Upper'].iloc[-1]:.2f}**. If the price punches through the top line, it might be overhyped and ready to drop.
    
    *   **2. MACD Momentum**: 
        *   *What it is:* This tracks market speed. When the purple line crosses *above* the red line, it's a **"Buy Signal"** showing upward momentum. When it crosses *below*, the price speed is slowing down.
        
    *   **3. Relative Strength Space (RSI)**: 
        *   *What it is:* A thermometer measuring market fever from 0 to 100. Current score: **{eq_data['RSI'].iloc[-1]:.2f}**.
        *   *How to read it:* If the score is **above 70**, the asset is "Overbought" (too hot, people are greedy, expect a pullback). If it's **below 30**, it is "Oversold" (cheap, people are panicking, might be a good time to buy).
        
    *   **4. Chaikin Money Flow (CMF)**: 
        *   *What it is:* Tracks big institutional money blocks moving into or out of the asset. Current flow score: **{eq_data['CMF'].iloc[-1]:.2f}**.
        *   *How to read it:* Anything **above 0.0** means institutional money is flowing *in* (bullish). Anything **below 0.0** means the big players are dumping their holdings.
        
    *   **5. ADX Trend Strength**: 
        *   *What it is:* Measures how powerful the current trend is, regardless of whether it's going up or down. Current score: **{eq_data['ADX'].iloc[-1]:.2f}**.
        *   *How to read it:* If this score is **below 20**, the market is walking sideways like a crab—avoid trading breakouts here. If it is **above 25**, a powerful explosive trend is taking off.
    """)

    with crypto_tab:
        crypto_ticker = st.selectbox("🎯 Target Crypto Asset Nodes", ["BTC-USD", "ETH-USD", "SOL-USD"])
        st.session_state['crypto_ticker'] = crypto_ticker
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

        with st.expander("🔍 Decentralized Infrastructure Analysis Insights", expanded=False):
            st.markdown(f"""
            * **Oscillator Levels**: Liquid Asset RSI sits at **{cr_data['RSI'].iloc[-1]:.2f}** units. (Value >70 indicates overbought conditions).
            * **Statistical Volatility**: Realized annualized volatility is sitting at **{(cr_data['Log_Return'].std() * np.sqrt(252) * 100):.2f}%**, highlighting significant retail distribution waves.
            """)


# ==============================================================================
# PAGE 3: STATISTICAL RISK & PROBABILISTIC MONTE CARLO
# ==============================================================================
elif page_selection == "🔮 3. Statistical Risk & Predictions":
    st.markdown("<h1 class='glow-text'>🔮 Stochastic Prediction & Monte Carlo Matrix</h1>", unsafe_allow_html=True)
    
    choice = st.selectbox("Select Target Portfolio Asset for Statistical Modeling", ["AAPL", "NVDA", "TSLA", "BTC-USD", "ETH-USD"])
    data = fetch_market_matrix(choice, lookback_days=user_lookback)
    
    daily_mean_ret = data['Log_Return'].mean()
    daily_std_ret = data['Log_Return'].std()
    sharpe = (daily_mean_ret / (daily_std_ret + 1e-9)) * np.sqrt(252)
    var_95 = np.percentile(data['Log_Return'], 5)
    roll_max = data['Close'].cummax()
    max_dd = ((data['Close'] - roll_max) / roll_max).min()
    
    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("🎯 Annualized Sharpe Ratio", f"{sharpe:.2f}")
    r_col2.metric("⚠️ 1-Day Value at Risk (95% VaR)", f"{var_95*100:.2f}%")
    r_col3.metric("📉 Maximum Peak-to-Trough Drawdown", f"{max_dd*100:.2f}%")
    
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

    with st.expander("💡 New Trader Guide: Understanding the 30-Day Probability Map", expanded=False):
        st.markdown(f"""
    Don't let all the chaotic lines scare you! This is a **Stochastic Forecast Simulator**. We took the historical price behavior of this asset and simulated 200 possible paths its price could take over the next 30 days. 
    
    Here is how to read your simulated future paths:
    
    *   **The Purple Line (The Median Case)**: This represents the exact middle path. If the market continues normal operation without major surprises, the asset is mathematically tracking toward **${p50[-1]:.2f}** in 30 days.
    *   **The Green Dash (The Dream Scenario - p95)**: This represents the best 5% of outcomes. If everything goes wonderfully well (great earnings, positive news), the price could climb up toward **${p95[-1]:.2f}**.
    *   **The Red Dash (The Worst-Case Floor - p5)**: This represents the absolute bottom 5% of outcomes. If panic breaks out or a major market crash occurs, history shows the price has strong structural emergency support down near **${p5[-1]:.2f}**.
    
    ⚠️ **What is 1-Day Value at Risk (VaR)?**
    *   Your current 1-day risk score is **{var_95*100:.2f}%**. 
    *   *In plain English:* If you invest **$10,000** into this asset, there is a 95% statistical probability that your worst loss in a normal single trading day will not exceed **${abs(var_95)*10000:.2f}**. If you lose more than that in a day, you are living through a highly rare "black swan" market crisis.
    """)

# ==============================================================================
# PAGE 4: MACRO-SECTOR DISTRIBUTION RADAR & PIE CHARTS
# ==============================================================================
elif page_selection == "🌐 4. Macro-Sector Distribution Radar":
    st.markdown("<h1 class='glow-text'>🌐 Portfolio Macro-Sector Allocation Analytics</h1>", unsafe_allow_html=True)
    
    sec_col, chart_col = st.columns([1, 1.5])
    
    with sec_col:
        st.markdown("""
        <div class='glass-card'>
            <h3>📊 Portfolio Weight Configuration</h3>
            <p>Customize sector exposure variables below to simulate global macroeconomic factor profiles.</p>
        </div>
        """, unsafe_allow_html=True)
        tech_w = st.slider("Technology Exposure %", 0, 100, 40)
        fin_w = st.slider("Finance Exposure %", 0, 100, 20)
        cons_w = st.slider("Consumer Discretionary %", 0, 100, 15)
        energy_w = st.slider("Energy Sector %", 0, 100, 15)
        crypto_w = st.slider("Alternative Assets / Crypto %", 0, 100, 10)
        
        sum_w = tech_w + fin_w + cons_w + energy_w + crypto_w
        if sum_w != 100:
            st.warning(f"⚠️ Sector Sum: {sum_w}%. Portfolio allocation should equal 100%. Adjust sliders.")
            
    with chart_col:
        sectors = ['Tech', 'Finance', 'Consumer', 'Energy', 'Crypto']
        weights = [tech_w, fin_w, cons_w, energy_w, crypto_w]
        
        # Plotly Donut Chart
        fig_donut = go.Figure(data=[go.Pie(labels=sectors, values=weights, hole=.4, marker=dict(colors=['#6366f1', '#a855f7', '#ec4899', '#3b82f6', '#10b981']))])
        fig_donut.update_layout(title="Global Sector Allocation (Weighted Donut Map)", template="plotly_dark", height=350)
        st.plotly_chart(fig_donut, use_container_width=True)
        
        # Plotly Polar Radar Chart
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=weights,
            theta=sectors,
            fill='toself',
            name='Configured Weights',
            line_color='#a855f7'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, title="Factor Loadings Polar Radar Map", template="plotly_dark", height=350)
        st.plotly_chart(fig_radar, use_container_width=True)

    with st.expander("💡 New Trader Guide: Balancing Your Allocation Radar", expanded=False):
        st.markdown(f"""
    Your pie chart and radar grid visualizes **Asset Allocation Risk**—essentially checking if you are putting too many of your eggs into one single basket.
    
    *   **Reading the Radar Shape**: Look at the purple web shape. A perfectly safe, balanced portfolio looks like a neat, round circle distributed across all sides. If your shape looks like a long, sharp spear pointing entirely toward **Tech** or **Crypto**, you are dangerously exposed.
    *   **The High-Beta Hazard**: Tech and Crypto assets are highly volatile. If your sliders put them above **50%** of your total portfolio, your net worth will swing up and down violently every morning. Balance them out with more conservative sectors like Finance or Energy to act as an anchor during economic storms.
    """)


# ==============================================================================
# PAGE 5: EXCHANGE LIQUIDITY PROFILE MAPS (SUNBURST & DUAL-BARS)
# ==============================================================================
elif page_selection == "📊 5. Exchange Liquidity Profile Maps":
    st.markdown("<h1 class='glow-text'>📊 Multi-Exchange Liquidity Structure Grid</h1>", unsafe_allow_html=True)
    
    # Hierarchical Sunburst Plotly Data
    data_sb = dict(
        labels=["Total Volume", "Coinbase", "Binance", "Nasdaq", "NYSE", "BTC/USD", "ETH/USD", "AAPL", "NVDA"],
        parents=["", "Total Volume", "Total Volume", "Total Volume", "Total Volume", "Coinbase", "Binance", "Nasdaq", "NYSE"],
        values=[1000, 350, 250, 220, 180, 200, 150, 120, 100]
    )
    
    fig_sb = px.sunburst(
        data_sb,
        names=data_sb['labels'],
        parents=data_sb['parents'],
        values=data_sb['values'],
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_sb.update_layout(title="Hierarchical Liquidity Breakdown Map (Sunburst)", template="plotly_dark", height=500)
    st.plotly_chart(fig_sb, use_container_width=True)

    with st.expander("🔍 Liquidity Concentration Diagnostics", expanded=False):
        st.markdown("""
        * **Sunburst Hierarchical Indexing**: Outer ring slices demonstrate the percentage of underlying volume matching across localized nodes.
        * **Institutional Order Inflow**: Centralized markets hold high structural dominance, while decentralized exchanges show higher localized liquidity shifts.
        """)


# ==============================================================================
# PAGE 6: MULTI-ASSET CROSS CORRELATIONS
# ==============================================================================
elif page_selection == "📈 6. Multi-Asset Cross Correlations":
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
            except Exception:
                pass
        df_corr = pd.DataFrame(returns_dict).dropna().corr()
        return df_corr

    corr_df = calculate_correlations(assets, user_lookback)
    
    fig_heat = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='Viridis',
        labels=dict(color="Correlation Score")
    )
    fig_heat.update_layout(title="Co-movement Matrix Heatmap (Returns Correlation)", template="plotly_dark", height=500)
    st.plotly_chart(fig_heat, use_container_width=True)

    with st.expander("💡 New Trader Guide: How to Cheat-Read the Heatmap", expanded=False):
        st.markdown("""
    The correlation heatmap acts like a mirror showing you which assets mimic each other's daily movements. It ranks relationships strictly between **-1.0** and **+1.0**.
    
    *   **What a +1.0 Score Means (Bright/Hot Blocks)**: Perfect harmony. If Asset A goes up, Asset B goes up at the exact same moment. For example, Bitcoin (BTC) and Ethereum (ETH) usually share a high positive score. Holding both does **not** protect your money because when one crashes, the other drops too.
    *   **What a 0.0 Score Means**: Zero relationship. The assets move completely independently of each other. This is exactly what you want to find to protect your cash.
    *   **What a Negative (-) Score Means (Dark Blocks)**: The ultimate insurance policy. If Asset A crashes, Asset B actually goes *up* to protect you. 
    
    📊 **Pro-Tip for Beginners**: To build a resilient portfolio that doesn't collapse all at once, choose assets from this matrix that have correlation numbers **lower than +0.4** relative to each other!
    """)


# ==============================================================================
# PAGE 7: HIGH-PERFORMANCE MARKOWITZ FRONTIER
# ==============================================================================
elif page_selection == "🧮 7. High-Performance Markowitz Frontier":
    st.markdown("<h1 class='glow-text'>🧮 Markowitz Mean-Variance Efficient Frontier</h1>", unsafe_allow_html=True)
    
    with st.spinner("Executing quadratic covariance optimization models..."):
        assets_portfolio = ["AAPL", "MSFT", "NVDA", "BTC-USD"]
        returns_list = []
        for asset in assets_portfolio:
            raw_p = yf.download(asset, start=dt.date.today() - dt.timedelta(days=user_lookback))
            if isinstance(raw_p.columns, pd.MultiIndex):
                raw_p.columns = raw_p.columns.get_level_values(0)
            returns_list.append(np.log(raw_p['Close'] / raw_p['Close'].shift(1)).dropna())
            
        returns_df = pd.concat(returns_list, axis=1, keys=assets_portfolio).dropna()
        
        num_portfolios = 500
        results = np.zeros((3, num_portfolios))
        weights_record = []
        
        mean_returns = returns_df.mean()
        cov_matrix = returns_df.cov()
        
        for i in range(num_portfolios):
            weights = np.random.random(len(assets_portfolio))
            weights /= np.sum(weights)
            weights_record.append(weights)
            
            p_return = np.sum(weights * mean_returns) * 252
            p_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
            
            results[0,i] = p_return
            results[1,i] = p_volatility
            results[2,i] = p_return / (p_volatility + 1e-9)
            
        fig_ef = go.Figure()
        fig_ef.add_trace(go.Scatter(
            x=results[1], y=results[0],
            mode='markers',
            marker=dict(color=results[2], colorscale='Electric', showscale=True, colorbar=dict(title="Sharpe")),
            text=[f"W: {list(np.round(w, 2))}" for w in weights_record]
        ))
        fig_ef.update_layout(title="Efficient Frontier Simulation Cloud", xaxis_title="Annualized Volatility", yaxis_title="Annualized Return", template="plotly_dark", height=500)
        st.plotly_chart(fig_ef, use_container_width=True)

        with st.expander("🔍 Mean-Variance Optimization Insights", expanded=False):
            st.markdown(f"""
            * **Maximum Sharpe Point**: The top-performing simulation reached a simulated Sharpe ratio of **{results[2].max():.2f}**.
            * **Risk-Minimizing Variance Bounds**: Low volatility allocations aggregate near the left-most edge of the plot.
            """)


# ==============================================================================
# PAGE 8: USER FEEDBACK & COMMENT SPACE (SQLITE BACKED)
# ==============================================================================
elif page_selection == "💬 8. Live Network Feedback Space":
    st.markdown("<h1 class='glow-text'>💬 Quant Terminal Feedback Room</h1>", unsafe_allow_html=True)
    
    form_col, list_col = st.columns([1, 1.2])
    
    with form_col:
        st.markdown("""
        <div class='glass-card'>
            <h3>💎 Log Your System Review</h3>
            <p>Write your detailed system feedback directly to our local secure database storage node.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("feedback_form"):
            name = st.text_input("Trader Name / Anonymous Handle", value="AnonymousQuant")
            satisfied = st.radio("Do you like this workspace terminal configuration?", ["Yes", "No, Needs Upgrades"])
            comment = st.text_area("Detailed Comments or Asset Requests")
            submit_feed = st.form_submit_button("Log Review Entry")
            
            if submit_feed and comment.strip():
                if insert_feedback(name, satisfied, comment):
                    st.success("Review logged successfully to SQLite!")
                    st.rerun()
                else:
                    st.error("Could not write feedback to database.")

    with list_col:
        st.markdown("<h3 class='glow-text'>📜 Live Network Reviews Feed</h3>", unsafe_allow_html=True)
        
        db_feedback = get_feedback()
        
        if not db_feedback:
            # Fallback Placeholders
            placeholders = [
                {"user": "QuantAlpha", "like": "Yes", "comment": "The simulation tools and mathematical models perform exceptionally well.", "time": "2026-07-10"},
                {"user": "CryptoWhale_99", "like": "Yes", "comment": "Volume analysis parameters render perfectly across continuous ticks.", "time": "2026-07-11"}
            ]
            for review in placeholders:
                st.markdown(f"""
                <div class='glass-card'>
                    <div style="display:flex; justify-content:space-between;">
                        <b>👤 {review['user']}</b>
                        <span style="color:#a855f7;">{review['time']}</span>
                    </div>
                    <p style="margin-top:8px;">{review['comment']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            for row in db_feedback:
                user, like, comm, timestamp = row
                date_str = timestamp.split()[0] if timestamp else "Recent"
                st.markdown(f"""
                <div class='glass-card'>
                    <div style="display:flex; justify-content:space-between;">
                        <b>👤 {user}</b>
                        <span style="color:#6366f1;">{date_str}</span>
                    </div>
                    <p style="margin-top:8px;">{comm}</p>
                    <small style="color:rgba(255,255,255,0.4);">Satisfied: {like}</small>
                </div>
                """, unsafe_allow_html=True)
                
# ==============================================================================
# PAGE 9: ROOT ADMIN AUDIT PANEL
# ==============================================================================
elif page_selection == "🔑 9. Root Admin Audit":  # Must match the new text exactly
    st.markdown("<h1 class='glow-text'>🔑 Oracle Terminal - Master Admin Directory</h1>", unsafe_allow_html=True)
    st.caption("Authorized Node Operations Only")

    password_input = st.text_input("Enter Root Master Password", type="password")

    if password_input == "oracleadmin2026":
        st.success("Root identity cleared! Extracting master user databases...")
        
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
        if password_input != "":
            st.error("Access Denied: Admin verification pending.")

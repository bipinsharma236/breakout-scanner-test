import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Setup
st.set_page_config(page_title="High-Probability Setup Scanner", layout="wide")
st.title("🚀 Profit Setup Scanner (Daily)")

@st.cache_data
def load_tickers(index):
    sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    nasdaq = pd.read_html("https://en.wikipedia.org/wiki/NASDAQ-100")[4]
    return {
        "S&P 500": sp500['Symbol'].tolist(),
        "NASDAQ 100": nasdaq['Ticker'].tolist()
    }

# User selection
index_data = load_tickers("index")
index_choice = st.selectbox("Select Index", ["S&P 500", "NASDAQ 100", "Custom"])
if index_choice == "Custom":
    custom_input = st.text_input("Enter custom tickers:", "SPY, QQQ, TSLA, AAPL")
    tickers = [x.strip().upper() for x in custom_input.split(",")]
else:
    tickers = index_data[index_choice]

selected_setups = st.multiselect(
    "Select setup types to scan for:",
    ["EMA Trend", "RSI Reversal", "Inside Day", "Volume Spike"],
    default=["EMA Trend"]
)

# Scanner logic
def analyze_ticker(ticker):
    try:
        df = yf.download(ticker, interval='1d', period='6mo', progress=False)
        if df.empty or len(df) < 21:
            return None, None

        df['EMA_8'] = df['Close'].ewm(span=8).mean()
        df['EMA_21'] = df['Close'].ewm(span=21).mean()
        df['RSI'] = df['Close'].rolling(window=14).apply(lambda x: talib.RSI(x, timeperiod=14)[-1] if len(x) >= 14 else None)
        df['Volume_Avg'] = df['Volume'].rolling(10).mean()

        last = df.iloc[-1]
        prev = df.iloc[-2]

        signals = []

        # 📈 EMA Trend
        if (
            last['EMA_8'] > last['EMA_21'] and
            last['EMA_21'] > df['EMA_21'].iloc[-3]  # Rising EMA21
        ):
            signals.append("📈 EMA Trend")

        # 🔄 RSI Reversal
        if last['RSI'] is not None and last['RSI'] < 35:
            signals.append("🔄 RSI Oversold")

        # 🔍 Inside Day
        if last['High'] < prev['High'] and last['Low'] > prev['Low']:
            signals.append("🔍 Inside Day")

        # 💣 Volume Spike
        if last['Volume'] > 1.5 * last['Volume_Avg']:
            signals.append("💣 Volume Spike")

        return df, signals if signals else None

    except Exception as e:
        return None, None

# Run scan
found_setups = []

with st.spinner("Scanning tickers..."):
    for ticker in tickers:
        df, signals = analyze_ticker(ticker)
        if signals:
            found_setups.append((ticker, signals, df))

# Show results
st.subheader(f"✅ Setups Found: {len(found_setups)}")

for ticker, signals, df in found_setups:
    st.markdown(f"### {ticker} — {' | '.join(signals)}")
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(df['Close'], label='Price', linewidth=1.5)
    ax.plot(df['EMA_8'], label='EMA 8')
    ax.plot(df['EMA_21'], label='EMA 21')
    ax.set_title(f"{ticker} — Daily")
    ax.legend()
    st.pyplot(fig)

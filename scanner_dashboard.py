import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- SETUP ---
st.set_page_config(page_title="Market Breakout Scanner", layout="wide")
st.title("📈 S&P 500 & NASDAQ Breakout Scanner")
st.markdown(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- DATA SOURCES ---
@st.cache_data
def load_tickers(index):
    if index == "S&P 500":
        table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
        return table['Symbol'].tolist()
    elif index == "NASDAQ 100":
        table = pd.read_html("https://en.wikipedia.org/wiki/NASDAQ-100")[4]
        return table['Ticker'].tolist()
    else:
        return []

# --- USER SELECTION ---
index_choice = st.selectbox("Select Index to Scan", ["S&P 500", "NASDAQ 100", "Custom"])
if index_choice == "Custom":
    custom_input = st.text_input("Enter tickers separated by commas", "SPY, QQQ, TSLA, AAPL")
    tickers = [x.strip().upper() for x in custom_input.split(",")]
else:
    tickers = load_tickers(index_choice)

# --- SCANNER LOGIC ---
def analyze_ticker(ticker):
    try:
        df = yf.download(ticker, interval='1d', period='6mo', progress=False)
        if df.empty or len(df) < 21:
            return None, None

        df['EMA_8'] = df['Close'].ewm(span=8).mean()
        df['EMA_21'] = df['Close'].ewm(span=21).mean()
        df['BB_Upper'] = df['Close'].rolling(20).mean() + 2 * df['Close'].rolling(20).std()

        last_close = df['Close'].iloc[-1]
        last_bb = df['BB_Upper'].iloc[-1]
        last_ema8 = df['EMA_8'].iloc[-1]
        last_ema21 = df['EMA_21'].iloc[-1]

        if pd.notna(last_bb) and pd.notna(last_ema8) and pd.notna(last_ema21):
            breakout = (last_close > last_bb) and (last_ema8 > last_ema21)
        else:
            breakout = False

        data = {
            'Close': round(last_close, 2),
            'EMA_8': round(last_ema8, 2),
            'EMA_21': round(last_ema21, 2),
            'BB_Upper': round(last_bb, 2),
            'Breakout Signal': '✅ YES' if breakout else '❌ NO'
        }

        return df, data
    except:
        return None, None

# --- SCAN & DISPLAY ---
breakout_tickers = []

for ticker in st.spinner("Scanning tickers..."), tickers:
    df, result = analyze_ticker(ticker)
    if df is None:
        continue
    if result["Breakout Signal"] == "✅ YES":
        breakout_tickers.append((ticker, result, df))

# --- RESULTS ---
st.subheader(f"📊 Breakout Results — {len(breakout_tickers)} tickers found")
for ticker, result, df in breakout_tickers:
    st.markdown(f"### {ticker} — {result['Breakout Signal']}")
    st.write(result)

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(df['Close'], label='Price', linewidth=1.5)
    ax.plot(df['EMA_8'], label='EMA 8')
    ax.plot(df['EMA_21'], label='EMA 21')
    ax.plot(df['BB_Upper'], label='Upper BB', linestyle=':')
    ax.set_title(f"{ticker} — Daily Chart")
    ax.legend()
    st.pyplot(fig)

if not breakout_tickers:
    st.info("No breakout setups detected in current list.")

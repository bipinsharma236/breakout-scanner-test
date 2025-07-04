import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="📊 Breakout Scanner", layout="wide")
st.title("🚨 Real-Time & Weekend Breakout Scanner")

# Mode selection
mode = st.radio("Select Mode:", ["📈 Intraday Live Scanner", "📅 Weekend Setup Scanner"])

# Ticker input (comma-separated)
tickers_input = st.text_input("Enter tickers to scan (comma-separated)", value="SPY, QQQ, TSLA, AAPL, MSFT")
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

def analyze_intraday(ticker):
    df = yf.download(ticker, interval='15m', period='1d')
    if df.empty or len(df) < 21:
        return None, None

    df['EMA_8'] = df['Close'].ewm(span=8).mean()
    df['EMA_21'] = df['Close'].ewm(span=21).mean()
    df['VWAP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['BB_Upper'] = df['Close'].rolling(20).mean() + 2 * df['Close'].rolling(20).std()

    last = df.iloc[-1]
    breakout = (last['Close'] > last['BB_Upper']) and (last['Close'] > last['VWAP']) and (last['EMA_8'] > last['EMA_21'])
    signal = '✅ YES' if breakout else '❌ NO'

    return df, {
        'Price': round(last['Close'], 2),
        'EMA_8': round(last['EMA_8'], 2),
        'EMA_21': round(last['EMA_21'], 2),
        'VWAP': round(last['VWAP'], 2),
        'BB_Upper': round(last['BB_Upper'], 2),
        'Breakout': signal
    }

def analyze_weekend(ticker):
    df = yf.download(ticker, interval='1d', period='3mo')
    if df.empty or len(df) < 21:
        return None, None

    df['EMA_8'] = df['Close'].ewm(span=8).mean()
    df['EMA_21'] = df['Close'].ewm(span=21).mean()
    df['BB_Upper'] = df['Close'].rolling(20).mean() + 2 * df['Close'].rolling(20).std()

    last = df.iloc[-1]
    breakout = (last['Close'] > last['BB_Upper']) and (last['EMA_8'] > last['EMA_21'])
    signal = '✅ YES' if breakout else '❌ NO'

    return df, {
        'Close': round(last['Close'], 2),
        'EMA_8': round(last['EMA_8'], 2),
        'EMA_21': round(last['EMA_21'], 2),
        'BB_Upper': round(last['BB_Upper'], 2),
        'Breakout Signal': signal
    }

# Scanner Execution
for ticker in tickers:
    if mode == "📈 Intraday Live Scanner":
        df, result = analyze_intraday(ticker)
        chart_title = f"{ticker} (15m)"
    else:
        df, result = analyze_weekend(ticker)
        chart_title = f"{ticker} (Daily)"

    if df is not None:
        st.subheader(f"📊 {ticker} — {result.get('Breakout', result.get('Breakout Signal'))}")
        st.write(result)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df['Close'], label='Price', linewidth=1.5)
        if 'EMA_8' in df: ax.plot(df['EMA_8'], label='EMA 8')
        if 'EMA_21' in df: ax.plot(df['EMA_21'], label='EMA 21')
        if 'VWAP' in df: ax.plot(df['VWAP'], label='VWAP', linestyle='--')
        if 'BB_Upper' in df: ax.plot(df['BB_Upper'], label='Upper BB', linestyle=':')
        ax.set_title(chart_title)
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning(f"{ticker}: Not enough data or unavailable.")

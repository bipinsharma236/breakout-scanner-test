import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="📈 Real-Time Breakout Scanner", layout="wide")
st.title("📊 Real-Time Breakout Scanner with Charts")
st.markdown(f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")

watchlist = ['SPY', 'QQQ', 'TSLA', 'AAPL']
interval = '15m'
period = '1d'

def analyze(ticker):
    df = yf.download(ticker, interval=interval, period=period)
    if df.empty or len(df) < 21:
        return None, None

    df['EMA_8'] = df['Close'].ewm(span=8).mean()
    df['EMA_21'] = df['Close'].ewm(span=21).mean()
    df['VWAP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['BB_Upper'] = df['Close'].rolling(20).mean() + 2 * df['Close'].rolling(20).std()

    last = df.iloc[-1]
    breakout = (
        last['Close'] > last['BB_Upper'] and
        last['Close'] > last['VWAP'] and
        last['EMA_8'] > last['EMA_21']
    )
    
    signal = '✅ YES' if breakout else '❌ NO'

    return df, {
        'Price': round(last['Close'], 2),
        'EMA_8': round(last['EMA_8'], 2),
        'EMA_21': round(last['EMA_21'], 2),
        'VWAP': round(last['VWAP'], 2),
        'BB_Upper': round(last['BB_Upper'], 2),
        'Breakout': signal
    }

for ticker in watchlist:
    df, data = analyze(ticker)
    if df is None:
        continue

    st.subheader(f"📍 {ticker} — Breakout: {data['Breakout']}")
    st.write(data)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['Close'], label='Price', linewidth=1.5)
    ax.plot(df['EMA_8'], label='EMA 8')
    ax.plot(df['EMA_21'], label='EMA 21')
    ax.plot(df['VWAP'], label='VWAP', linestyle='--')
    ax.plot(df['BB_Upper'], label='Upper BB', linestyle=':')
    ax.set_title(f"{ticker} Chart")
    ax.legend()
    st.pyplot(fig)

import os
import yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask, jsonify
from flask_cors import CORS
from predict import predict_stock

app = Flask(__name__)
CORS(app)

# -------------------------------
# ML Prediction Endpoint
@app.route("/predict/<stock>")
def predict(stock):
    try:
        result = predict_stock(stock)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Candlestick + Volume Data
@app.route('/history/<ticker>/<period>')
def get_history(ticker, period):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return jsonify([])

        # 1. Reset index so 'Date' becomes a standard column
        hist = hist.reset_index()
        
        # 2. Convert Pandas Timestamps to standard text strings
        if 'Date' in hist.columns:
            hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
        elif 'Datetime' in hist.columns:
            hist['Datetime'] = hist['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
        # 3. Clean up NaN or Infinity values that break JSON parsing
        hist = hist.replace([np.nan, np.inf, -np.inf], None)
        
        # 4. Return as clean JSON
        return jsonify(hist.to_dict(orient='records'))
        
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Technical Indicators (RSI + MACD)
@app.route("/indicators/<stock>")
def indicators(stock):
    try:
        # Changed from download() to Ticker().history() for safety
        ticker = yf.Ticker(stock)
        data = ticker.history(period="6mo")

        if data.empty:
            return jsonify([])

        close = data['Close']

        # RSI calculation
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # MACD calculation
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()

        result = []
        for i in range(len(data)):
            # Safely handle NaN values
            rsi_val = float(rsi.iloc[i]) if not pd.isna(rsi.iloc[i]) else None
            macd_val = float(macd.iloc[i]) if not pd.isna(macd.iloc[i]) else None
            signal_val = float(signal.iloc[i]) if not pd.isna(signal.iloc[i]) else None

            result.append({
                "time": data.index[i].strftime("%Y-%m-%d"),
                "rsi": rsi_val,
                "macd": macd_val,
                "signal": signal_val
            })

        return jsonify(result)

    except Exception as e:
        print(f"Error fetching indicators for {stock}: {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Top Gainers / Losers
@app.route("/market")
def market():
    stocks = ["RELIANCE.NS", "INFY.NS", "TCS.NS", "HDFCBANK.NS"]
    result = []

    for s in stocks:
        try:
            # Changed to Ticker().history() and increased period to avoid weekend missing data
            ticker = yf.Ticker(s)
            data = ticker.history(period="5d")

            if data.empty or len(data) < 2:
                continue

            latest = float(data['Close'].iloc[-1])
            prev = float(data['Close'].iloc[-2])

            change = latest - prev
            percent = (change / prev) * 100

            result.append({
                "stock": s,
                "price": round(latest, 2),
                "change": round(change, 2),
                "percent": round(percent, 2)
            })

        except Exception as e:
            print(f"Market error for {s}: {e}")
            continue

    return jsonify(result)

# -------------------------------
# API Home
@app.route("/")
def home():
    return jsonify({
        "message": "BullTrade API is running",
        "endpoints": [
            "/predict/<stock>",
            "/history/<stock>/<range>",
            "/market",
            "/indicators/<stock>",
            "/live/<stock>"
        ]
    })

# -------------------------------
# Live Price
@app.route("/live/<stock>")
def live_price(stock):
    try:
        ticker = yf.Ticker(stock)
        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            return jsonify({})

        latest_price = float(data['Close'].iloc[-1])

        return jsonify({
            "stock": stock,
            "price": round(latest_price, 2)
        })

    except Exception as e:
        print(f"Live price error for {stock}: {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
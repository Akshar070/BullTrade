import os

from flask import Flask, jsonify
from flask_cors import CORS
import yfinance as yf
from flask import jsonify
import pandas as pd
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
        return jsonify({"error": str(e)})


# Candlestick + Volume Data
@app.route('/history/<ticker>/<period>')
def history(ticker, period):
    try:
        # 1. Fetch the data
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        # 2. Reset the index so 'Date' becomes a regular column
        hist = hist.reset_index()
        
        # 3. Convert the Pandas Timestamps to standard strings (Crucial Step)
        if 'Date' in hist.columns:
            hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
        elif 'Datetime' in hist.columns: # Sometimes yfinance uses Datetime for shorter periods
            hist['Datetime'] = hist['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # 4. Convert to a dictionary and send as JSON
        # orient='records' makes it a clean list of objects for your frontend
        return jsonify(hist.to_dict(orient='records'))

    except Exception as e:
        # This will print the exact error to your Render logs if it fails again
        print(f"Error fetching history: {e}") 
        return jsonify({"error": "Failed to fetch stock data"}), 500


# Technical Indicators
# RSI + MACD
@app.route("/indicators/<stock>")
def indicators(stock):

    import pandas as pd

    try:

        data = yf.download(stock, period="6mo")

        if data.empty:
            return jsonify([])

        close = data["Close"]

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

            rsi_val = None
            macd_val = None
            signal_val = None

            if not pd.isna(rsi.iloc[i]):
                rsi_val = float(rsi.iloc[i])

            if not pd.isna(macd.iloc[i]):
                macd_val = float(macd.iloc[i])

            if not pd.isna(signal.iloc[i]):
                signal_val = float(signal.iloc[i])

            result.append({
                "time": data.index[i].strftime("%Y-%m-%d"),
                "rsi": rsi_val,
                "macd": macd_val,
                "signal": signal_val
            })

        return jsonify(result)

    except Exception as e:

        return jsonify({"error": str(e)})


# Top Gainers / Losers
@app.route("/market")
def market():

    stocks = ["RELIANCE.NS","INFY.NS","TCS.NS","HDFCBANK.NS"]

    result = []

    for s in stocks:

        try:

            data = yf.download(s,period="2d")

            if data.empty or len(data)<2:
                continue

            latest=float(data.Close.iloc[-1])
            prev=float(data.Close.iloc[-2])

            change=latest-prev
            percent=(change/prev)*100

            result.append({
                "stock":s,
                "price":latest,
                "change":change,
                "percent":percent
            })

        except:
            continue

    return jsonify(result)

@app.route("/")
def home():
    return {
        "message": "BullTrade API is running",
        "endpoints": [
            "/predict/<stock>",
            "/history/<stock>/<range>",
            "/market"
        ]
    }

@app.route("/live/<stock>")
def live_price(stock):

    try:

        data = yf.download(stock, period="1d", interval="1m")

        if data.empty:
            return jsonify({})

        latest_price = float(data.Close.iloc[-1])

        return jsonify({
            "stock": stock,
            "price": latest_price
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
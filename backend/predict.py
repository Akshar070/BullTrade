import yfinance as yf
import joblib
import pandas as pd

lr_model = joblib.load("models/linear_model.pkl")
rf_model = joblib.load("models/rf_model.pkl")

def predict_stock(stock):

    data = yf.download(stock, period="3mo")

    if data.empty:
        return {"error":"No stock data"}

    data['Prev Close'] = data['Close'].shift(1)
    data['MA10'] = data['Close'].rolling(10).mean()
    data['MA50'] = data['Close'].rolling(50).mean()

    data = data.dropna()

    latest = data.iloc[-1]

    features = [[
        float(latest['Prev Close']),
        float(latest['MA10']),
        float(latest['MA50']),
        float(latest['Volume'])
    ]]

    lr_pred = lr_model.predict(features)[0]
    rf_pred = rf_model.predict(features)[0]
    
    current_price = float(latest["Close"])

    direction = "Rise 📈" if rf_pred > current_price else "Fall 📉"

    return {
        "current_price":current_price,
        "lr_prediction":float(lr_pred),
        "rf_prediction":float(rf_pred),
        "direction":direction,
        "time": data.index[-1].strftime("%Y-%m-%d")
    }
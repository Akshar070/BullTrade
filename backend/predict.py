import yfinance as yf
import joblib
import pandas as pd

lr_model = joblib.load("models/linear_model.pkl")
rf_model = joblib.load("models/rf_model.pkl")

def predict_stock(stock):

    data = yf.download(stock, period="1y")

    if data.empty:
        return {"error": "No data found"}

    data["MA10"] = data["Close"].rolling(10).mean()
    data["MA50"] = data["Close"].rolling(50).mean()

    data.dropna(inplace=True)

    latest = data.iloc[-1]

    current_price = float(latest["Close"].item())
    ma10 = float(latest["MA10"].item())
    ma50 = float(latest["MA50"].item())
    volume = float(latest["Volume"].item())

    features = [[current_price, ma10, ma50, volume]]

    lr_pred = float(lr_model.predict(features)[0])
    rf_pred = float(rf_model.predict(features)[0])

    direction = "Rise 📈" if rf_pred > current_price else "Fall 📉"

    return {
        "current_price": round(current_price,2),
        "lr_prediction": round(lr_pred,2),
        "rf_prediction": round(rf_pred,2),
        "direction": direction
    }
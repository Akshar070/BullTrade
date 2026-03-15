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

    features = [[
        float(latest["Close"]),
        float(latest["MA10"]),
        float(latest["MA50"]),
        float(latest["Volume"])
    ]]

    lr_pred = lr_model.predict(features)[0]
    rf_pred = rf_model.predict(features)[0]

    current_price = float(latest["Close"])

    direction = "Rise 📈" if rf_pred > current_price else "Fall 📉"

    return {
        "current_price": round(current_price,2),
        "lr_prediction": round(float(lr_pred),2),
        "rf_prediction": round(float(rf_pred),2),
        "direction": direction
    }
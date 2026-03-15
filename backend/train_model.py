import pandas as pd
import yfinance as yf
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

stock = "RELIANCE.NS"

data = yf.download(stock, period="5y")

# Feature Engineering
data['Prev Close'] = data['Close'].shift(1)
data['MA10'] = data['Close'].rolling(10).mean()
data['MA50'] = data['Close'].rolling(50).mean()

data = data.dropna()

X = data[['Prev Close','MA10','MA50','Volume']]
y = data['Close'].values.ravel()

X_train,X_test,y_train,y_test = train_test_split(
X,y,test_size=0.2,random_state=42
)

lr = LinearRegression()
rf = RandomForestRegressor(n_estimators=100)

lr.fit(X_train,y_train)
rf.fit(X_train,y_train)

joblib.dump(lr,"models/linear_model.pkl")
joblib.dump(rf,"models/rf_model.pkl")

print("Models trained successfully")
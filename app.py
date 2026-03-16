import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("Minervini Trend Template Scanner (Polygon)")

API_KEY = st.secrets["POLYGON_API_KEY"]

# Charger les tickers S&P500
sp500 = pd.read_csv(
    "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
)

tickers = sp500["Symbol"].tolist()

end = datetime.today()
start = end - timedelta(days=400)

results = []

progress = st.progress(0)

def get_polygon_data(ticker):

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start.date()}/{end.date()}?adjusted=true&limit=500&apiKey={API_KEY}"

    r = requests.get(url)

    if r.status_code != 200:
        return None

    data = r.json()

    if "results" not in data:
        return None

    df = pd.DataFrame(data["results"])

    df["date"] = pd.to_datetime(df["t"], unit="ms")
    df.set_index("date", inplace=True)

    df.rename(columns={"c":"close","v":"volume"}, inplace=True)

    return df[["close","volume"]]


for i, ticker in enumerate(tickers):

    df = get_polygon_data(ticker)

    if df is None or len(df) < 200:
        continue

    close = df["close"]

    ma50 = close.rolling(50).mean()
    ma150 = close.rolling(150).mean()
    ma200 = close.rolling(200).mean()

    price = close.iloc[-1]

    low_52 = close.min()
    high_52 = close.max()

    ma200_20 = ma200.iloc[-20]

    stock_return = (close.iloc[-1] / close.iloc[0]) - 1

    cond1 = price > ma150.iloc[-1] and price > ma200.iloc[-1]
    cond2 = ma150.iloc[-1] > ma200.iloc[-1]
    cond3 = ma200.iloc[-1] > ma200_20
    cond4 = ma50.iloc[-1] > ma150.iloc[-1] and ma50.iloc[-1] > ma200.iloc[-1]
    cond5 = price > ma50.iloc[-1]
    cond6 = price >= 1.3 * low_52
    cond7 = price >= 0.75 * high_52
    cond8 = stock_return > 0

    if all([cond1,cond2,cond3,cond4,cond5,cond6,cond7,cond8]):

        results.append({
            "Ticker": ticker,
            "Price": round(price,2),
            "Return 1Y %": round(stock_return*100,2),
            "52W High": round(high_52,2),
            "52W Low": round(low_52,2)
        })

    progress.progress((i+1)/len(tickers))


df_results = pd.DataFrame(results)

st.subheader("Stocks Matching Minervini Trend Template")

if len(df_results) > 0:

    df_results = df_results.sort_values("Return 1Y %", ascending=False)

    st.dataframe(df_results, use_container_width=True)

else:

    st.write("No stocks found.")

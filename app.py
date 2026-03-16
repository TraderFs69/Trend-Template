import streamlit as st
import pandas as pd
import requests

st.title("Polygon Test")

# récupérer la clé
API_KEY = st.secrets["POLYGON_API_KEY"]

ticker = st.text_input("Ticker", "AAPL")

url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/2024-01-01/2024-12-31?adjusted=true&apiKey={API_KEY}"

r = requests.get(url)

data = r.json()

if "results" in data:

    df = pd.DataFrame(data["results"])

    df["date"] = pd.to_datetime(df["t"], unit="ms")

    df.rename(columns={
        "c":"Close",
        "o":"Open",
        "h":"High",
        "l":"Low",
        "v":"Volume"
    }, inplace=True)

    st.dataframe(df)

else:

    st.write("No data returned")

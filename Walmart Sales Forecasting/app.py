import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from pathlib import Path

st.set_page_config(
    page_title="Walmart Sales Forecasting",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Walmart Sales Forecasting Dashboard")
st.write("Forecast Walmart weekly sales using Prophet with seasonality and holiday effects.")

uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.sidebar.success("Uploaded dataset loaded!")
else:
    DATA_PATH = Path(__file__).parent / "Walmart_Store_sales.csv"
    data = pd.read_csv(DATA_PATH)
    st.sidebar.info("Using default Walmart dataset.")

required_columns = ["Date", "Weekly_Sales"]

if not all(col in data.columns for col in required_columns):
    st.error("Dataset must contain `Date` and `Weekly_Sales` columns.")
    st.stop()

data["Date"] = pd.to_datetime(data["Date"], dayfirst=True, errors="coerce")
data = data.dropna(subset=["Date", "Weekly_Sales"])

st.sidebar.header("⚙️ Controls")

if "Store" in data.columns:
    store_option = st.sidebar.selectbox(
        "Select Store",
        ["All Stores"] + sorted(data["Store"].unique().tolist())
    )

    if store_option != "All Stores":
        data = data[data["Store"] == store_option]

forecast_weeks = st.sidebar.slider(
    "Forecast horizon for future weeks",
    min_value=4,
    max_value=52,
    value=20
)

split_date = st.sidebar.date_input(
    "Train-test split date",
    value=pd.to_datetime("2012-01-01")
)

agg = data.groupby("Date")["Weekly_Sales"].sum().reset_index()
agg.columns = ["ds", "y"]
agg = agg.sort_values("ds")

st.subheader("🔍 Dataset Preview")
st.dataframe(data.head())

st.subheader("📈 Sales Trend")
st.line_chart(agg.set_index("ds"))

train = agg[agg["ds"] < pd.to_datetime(split_date)]
test = agg[agg["ds"] >= pd.to_datetime(split_date)]

if len(train) < 20:
    st.warning("Not enough training data. Choose an earlier split date.")
    st.stop()

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)

model.add_country_holidays(country_name="US")
model.fit(train)

future = model.make_future_dataframe(periods=len(test) + forecast_weeks, freq="W")
forecast = model.predict(future)

pred_test = forecast.iloc[len(train):len(train) + len(test)]

if len(test) > 0:
    mae = mean_absolute_error(test["y"], pred_test["yhat"])
    mape = np.mean(
        np.abs((test["y"].values - pred_test["yhat"].values) / test["y"].values)
    ) * 100

    col1, col2 = st.columns(2)

    with col1:
        st.metric("MAE", f"{mae:,.2f}")

    with col2:
        st.metric("MAPE", f"{mape:.2f}%")

    st.subheader("📉 Forecast vs Actual")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(test["ds"], test["y"], label="Actual")
    ax.plot(pred_test["ds"], pred_test["yhat"], label="Predicted")
    ax.set_title("Prophet Forecast vs Actual")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weekly Sales")
    ax.legend()
    st.pyplot(fig)

st.subheader("🔮 Full Prophet Forecast")

fig2 = model.plot(forecast)
st.pyplot(fig2)

st.subheader("📋 Future Forecast Data")

future_forecast = forecast.tail(forecast_weeks)[["ds", "yhat", "yhat_lower", "yhat_upper"]]

st.dataframe(future_forecast)

csv = future_forecast.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Future Forecast CSV",
    data=csv,
    file_name="future_forecast_results.csv",
    mime="text/csv"
)

st.subheader("🧠 Project Summary")

st.write("""
This application uses Prophet to forecast Walmart weekly sales.
The model includes yearly seasonality, weekly seasonality, and US holiday effects.
Users can upload new data, select a store, adjust the forecast horizon, and download forecast results.
""")

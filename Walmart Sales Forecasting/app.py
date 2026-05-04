import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from pathlib import Path

st.set_page_config(page_title="Walmart Sales Forecasting", layout="centered")

st.title("📊 Walmart Sales Forecasting App")
st.write("Upload a CSV file or use the default Walmart sales dataset.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.success("Uploaded dataset loaded successfully!")
else:
    DATA_PATH = Path(__file__).parent / "Walmart_Store_sales.csv"
    data = pd.read_csv(DATA_PATH)
    st.info("Using default Walmart dataset.")

st.subheader("Dataset Preview")
st.dataframe(data.head())

required_columns = ["Date", "Weekly_Sales"]

if not all(col in data.columns for col in required_columns):
    st.error("Dataset must contain 'Date' and 'Weekly_Sales' columns.")
    st.stop()

data["Date"] = pd.to_datetime(data["Date"], dayfirst=True, errors="coerce")
data = data.dropna(subset=["Date", "Weekly_Sales"])

agg = data.groupby("Date")["Weekly_Sales"].sum().reset_index()
agg.columns = ["ds", "y"]
agg = agg.sort_values("ds")

st.subheader("📈 Aggregated Sales Data")
st.line_chart(agg.set_index("ds"))

split_date = st.date_input(
    "Select train-test split date",
    value=pd.to_datetime("2012-01-01")
)

train = agg[agg["ds"] < pd.to_datetime(split_date)]
test = agg[agg["ds"] >= pd.to_datetime(split_date)]

if len(train) < 20 or len(test) < 5:
    st.warning("Not enough train/test data. Please choose a better split date.")
    st.stop()

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)

model.add_country_holidays(country_name="US")
model.fit(train)

future = model.make_future_dataframe(periods=len(test), freq="W")
forecast = model.predict(future)

pred = forecast.tail(len(test))

mae = mean_absolute_error(test["y"], pred["yhat"])
mape = np.mean(
    np.abs((test["y"].values - pred["yhat"].values) / test["y"].values)
) * 100

st.subheader("📊 Model Evaluation")
st.write(f"MAE: {mae:.2f}")
st.write(f"MAPE: {mape:.2f}%")

st.subheader("📉 Forecast vs Actual")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(test["ds"], test["y"], label="Actual")
ax.plot(pred["ds"], pred["yhat"], label="Predicted")
ax.set_title("Prophet Forecast vs Actual")
ax.set_xlabel("Date")
ax.set_ylabel("Weekly Sales")
ax.legend()
st.pyplot(fig)

st.subheader("🔮 Prophet Forecast")

fig2 = model.plot(forecast)
st.pyplot(fig2)

st.subheader("📋 Forecast Data")
forecast_table = pred[["ds", "yhat", "yhat_lower", "yhat_upper"]]
st.dataframe(forecast_table)

csv = forecast_table.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Forecast CSV",
    data=csv,
    file_name="forecast_results.csv",
    mime="text/csv"
)

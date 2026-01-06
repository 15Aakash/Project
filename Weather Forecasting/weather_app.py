import streamlit as st
import requests
import os
from datetime import datetime
import pandas as pd
from PIL import Image

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="Weather Forecasting",
    layout="wide"
)

# ------------------ API KEYS ------------------
# Works locally (.env / environment variable) AND Streamlit Cloud (Secrets)
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or st.secrets.get("OPENWEATHER_API_KEY")

if not WEATHER_API_KEY:
    st.error("❌ OpenWeather API key not found. Please set it in Streamlit Secrets.")
    st.stop()

# ------------------ SIDEBAR (LOGO + INPUT) ------------------
logo_path = os.path.join(os.path.dirname(__file__), "Logo.jpg")
if os.path.exists(logo_path):
    st.sidebar.image(Image.open(logo_path), width=130)

st.sidebar.title("Weather Forecasting with LLM")
city = st.sidebar.text_input("Enter city name", "palladam")
get_weather = st.sidebar.button("Get Weather")

# ------------------ FUNCTIONS ------------------
def get_current_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY}
    return requests.get(url, params=params).json()

def get_forecast(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": WEATHER_API_KEY}
    return requests.get(url, params=params).json()

def kelvin_to_celsius(k):
    return round(k - 273.15, 2)

def prepare_7_day_forecast(forecast_data):
    daily = {}

    for item in forecast_data["list"]:
        date = datetime.fromtimestamp(item["dt"]).strftime("%A, %B %d")

        temp_min = kelvin_to_celsius(item["main"]["temp_min"])
        temp_max = kelvin_to_celsius(item["main"]["temp_max"])
        desc = item["weather"][0]["description"].capitalize()

        if date not in daily:
            daily[date] = {
                "min": temp_min,
                "max": temp_max,
                "desc": desc
            }
        else:
            daily[date]["min"] = min(daily[date]["min"], temp_min)
            daily[date]["max"] = max(daily[date]["max"], temp_max)

    # Return EXACTLY 7 days
    return dict(list(daily.items())[:7])

def display_temperature_graph(weekly_data):
    dates = list(weekly_data.keys())
    temps = [weekly_data[d]["max"] for d in dates]

    df = pd.DataFrame({
        "Date": dates,
        "Temperature (°C)": temps
    })

    st.subheader("Temperature Trend (Next 7 Days)")
    st.line_chart(df.set_index("Date"))

# ------------------ MAIN UI ------------------
if get_weather:

    weather = get_current_weather(city)

    if weather.get("cod") != 200:
        st.error("❌ City not found. Please try another city.")
        st.stop()

    st.title(f"Weather Updates for {city}")

    # ---- Metrics ----
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Temperature", f"{kelvin_to_celsius(weather['main']['temp'])} °C")
        st.metric("Humidity", f"{weather['main']['humidity']}%")

    with col2:
        st.metric("Pressure", f"{weather['main']['pressure']} hPa")
        st.metric("Wind Speed", f"{weather['wind']['speed']} m/s")

    st.write(
        f"The current weather in your city is: "
        f"{weather['weather'][0]['description']} "
        f"with a temperature of {kelvin_to_celsius(weather['main']['temp'])} °C."
    )

    st.write("------------------------------------------------------------")

    # ---- Forecast ----
    forecast = get_forecast(weather["coord"]["lat"], weather["coord"]["lon"])
    weekly_data = prepare_7_day_forecast(forecast)

    # ---- GRAPH ----
    display_temperature_graph(weekly_data)

    st.write("------------------------------------------------------------")

    # ---- WEEKLY TABLE ----
    st.subheader("Weekly Weather Forecast")

    df = pd.DataFrame([
        {
            "Day": day,
            "Desc": data["desc"],
            "Min Temp": f"{data['min']} °C",
            "Max Temp": f"{data['max']} °C"
        }
        for day, data in weekly_data.items()
    ])

    st.dataframe(df, use_container_width=True)

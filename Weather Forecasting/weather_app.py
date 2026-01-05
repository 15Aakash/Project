import os
from dotenv import load_dotenv
import streamlit as st
import requests
from datetime import datetime

# Load local .env (ignored by git)
load_dotenv()

# Get API keys (local OR Streamlit Cloud)
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or st.secrets.get("OPENWEATHER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")


def get_weather_data(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY
    }
    response = requests.get(url, params=params, timeout=10)
    return response.json()


def get_weekly_forecast(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": WEATHER_API_KEY
    }
    response = requests.get(url, params=params, timeout=10)
    return response.json()


def display_weekly_forecast(data):
    st.subheader("📅 Weekly Forecast")

    shown_dates = set()
    for item in data.get("list", []):
        date = datetime.fromtimestamp(item["dt"]).strftime("%A, %B %d")

        if date in shown_dates:
            continue

        shown_dates.add(date)

        min_temp = item["main"]["temp_min"] - 273.15
        max_temp = item["main"]["temp_max"] - 273.15
        desc = item["weather"][0]["description"].capitalize()

        st.write(f"**{date}** — {desc}")
        st.write(f"🌡 Min: {min_temp:.1f}°C | Max: {max_temp:.1f}°C")
        st.divider()


def main():
    st.set_page_config(page_title="Weather Forecasting", layout="wide")

    # Sidebar
    st.sidebar.title("🌦 Weather Forecasting")
    city = st.sidebar.text_input("Enter city name", "London")

    if not WEATHER_API_KEY:
        st.error("❌ OPENWEATHER_API_KEY is missing.")
        st.stop()

    if st.sidebar.button("Get Weather"):
        weather_data = get_weather_data(city)

        # 🔐 SAFETY CHECK (THIS FIXES YOUR ERROR)
        if weather_data.get("cod") != 200:
            st.error(f"❌ Error fetching weather: {weather_data.get('message', 'Unknown error')}")
            st.stop()

        st.title(f"Weather Updates for {city}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("🌡 Temperature", f"{weather_data['main']['temp'] - 273.15:.1f} °C")
            st.metric("💧 Humidity", f"{weather_data['main']['humidity']} %")

        with col2:
            st.metric("🌬 Wind Speed", f"{weather_data['wind']['speed']} m/s")
            st.metric("📊 Pressure", f"{weather_data['main']['pressure']} hPa")

        lat = weather_data["coord"]["lat"]
        lon = weather_data["coord"]["lon"]

        forecast_data = get_weekly_forecast(lat, lon)

        if forecast_data.get("cod") == "200":
            display_weekly_forecast(forecast_data)
        else:
            st.warning("⚠ Weekly forecast unavailable.")


if __name__ == "__main__":
    main()

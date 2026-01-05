import os
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv

# Load .env locally (Streamlit Cloud will use st.secrets instead)
load_dotenv()


# ---------- API helpers ----------
def get_weather_data(city: str, api_key: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key}
    return requests.get(url, params=params, timeout=20).json()


def get_forecast_data(lat: float, lon: float, api_key: str) -> dict:
    # 5 day / 3 hour forecast
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": api_key}
    return requests.get(url, params=params, timeout=20).json()


def k_to_c(k: float) -> float:
    return k - 273.15


def generate_weather_description(data: dict) -> str:
    temp_c = k_to_c(data["main"]["temp"])
    desc = data["weather"][0]["description"]
    return f"The current weather in your city is: {desc} with a temperature of {temp_c:.1f} °C."


# ---------- UI helpers ----------
def show_logo():
    """
    Try multiple paths so it works both locally and on Streamlit Cloud.
    Your file is inside Weather Forecasting/Logo.jpg
    """
    possible_paths = [
        "Logo.jpg",
        "logo.jpg",
        "Weather Forecasting/Logo.jpg",
        "Weather Forecasting/logo.jpg",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            st.sidebar.image(p, width=140)
            return


def display_weekly_forecast_table(forecast: dict):
    if "list" not in forecast:
        st.error("No forecast data available!")
        return

    st.subheader("Weekly Weather Forecast")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**Day**")
    with c2:
        st.markdown("**Desc**")
    with c3:
        st.markdown("**Min_temp**")
    with c4:
        st.markdown("**Max_temp**")

    displayed_dates = set()

    for item in forecast["list"]:
        date_str = datetime.fromtimestamp(item["dt"]).strftime("%A, %B %d")
        if date_str in displayed_dates:
            continue
        displayed_dates.add(date_str)

        min_temp = k_to_c(item["main"]["temp_min"])
        max_temp = k_to_c(item["main"]["temp_max"])
        desc = item["weather"][0]["description"].capitalize()

        with c1:
            st.write(date_str)
        with c2:
            st.write(desc)
        with c3:
            st.write(f"{min_temp:.1f} °C")
        with c4:
            st.write(f"{max_temp:.1f} °C")


def display_temperature_graph(forecast: dict):
    """
    Graph (line chart) using the 5-day / 3-hour forecast:
    x-axis: datetime
    y-axis: temperature in °C
    """
    if "list" not in forecast:
        return

    times = []
    temps = []

    for item in forecast["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        temp_c = k_to_c(item["main"]["temp"])
        times.append(dt)
        temps.append(temp_c)

    st.subheader("Temperature Trend (Next 5 Days)")
    st.line_chart({"Temperature (°C)": temps}, x=times)


# ---------- Main app ----------
def main():
    st.set_page_config(page_title="Weather Forecasting", layout="wide")

    # Sidebar
    show_logo()
    st.sidebar.title("Weather Forecasting")
    city = st.sidebar.text_input("Enter city name", "London")
    submit = st.sidebar.button("Get Weather")

    # Read keys from .env (local) OR Streamlit secrets (cloud)
    weather_api_key = os.getenv("OPENWEATHER_API_KEY") or st.secrets.get("OPENWEATHER_API_KEY", None)

    if not weather_api_key:
        st.sidebar.error("OPENWEATHER_API_KEY missing. Add it to .env (local) or Streamlit Secrets (cloud).")
        st.stop()

    if submit:
        st.title(f"Weather Updates for {city}")

        with st.spinner("Fetching weather data..."):
            weather = get_weather_data(city, weather_api_key)

        cod = weather.get("cod")
        # OpenWeather returns cod sometimes as int or str
        if cod in (404, "404"):
            st.error("City not found or API error!")
            st.write(weather)  # helpful for debugging
            return

        # If API key invalid -> 401
        if cod in (401, "401"):
            st.error("Invalid API key (401). Check Streamlit Secrets / .env key value.")
            st.write(weather)
            return

        # Metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{k_to_c(weather['main']['temp']):.2f} °C")
            st.metric("Humidity", f"{weather['main']['humidity']}%")
        with col2:
            st.metric("Wind Speed", f"{weather['wind']['speed']} m/s")
            st.metric("Pressure", f"{weather['main']['pressure']} hPa")

        st.write(generate_weather_description(weather))

        lat = weather["coord"]["lat"]
        lon = weather["coord"]["lon"]

        with st.spinner("Fetching forecast..."):
            forecast = get_forecast_data(lat, lon, weather_api_key)

        # Graph first
        display_temperature_graph(forecast)

        # Weekly table
        display_weekly_forecast_table(forecast)


if __name__ == "__main__":
    main()

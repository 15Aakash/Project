import os
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv

# Load .env for local runs (Streamlit Cloud will use st.secrets instead)
load_dotenv()

st.set_page_config(page_title="Weather Forecasting", layout="wide")


# -------------------------
# API helpers
# -------------------------
def get_secret(key: str):
    """Get secrets from .env first, then Streamlit secrets."""
    return os.getenv(key) or st.secrets.get(key)


def get_weather_data(city, weather_api_key):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"appid": weather_api_key, "q": city}
    response = requests.get(base_url, params=params, timeout=15)
    return response.json()


def get_weekly_forecast(weather_api_key, lat, lon):
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": weather_api_key}
    response = requests.get(base_url, params=params, timeout=15)
    return response.json()


def generate_weather_description(data):
    """Mock response (no OpenAI call)."""
    temperature = data["main"]["temp"] - 273.15
    description = data["weather"][0]["description"]
    return (
        f"The current weather in your city is: {description} "
        f"with a temperature of {temperature:.1f} °C."
    )


# -------------------------
# UI helpers
# -------------------------
def display_weekly_forecast(data):
    try:
        if "list" not in data:
            st.error("No forecast data available!")
            return

        st.write("### Weekly Weather Forecast")
        displayed_dates = set()

        # Header row
        h1, h2, h3, h4 = st.columns([3, 3, 2, 2])
        h1.metric("", "Day")
        h2.metric("", "Desc")
        h3.metric("", "Min_temp")
        h4.metric("", "Max_temp")

        # Row-by-row output (this fixes the "weird layout")
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%A, %B %d")
            if date in displayed_dates:
                continue
            displayed_dates.add(date)

            min_temp = item["main"]["temp_min"] - 273.15
            max_temp = item["main"]["temp_max"] - 273.15
            description = item["weather"][0]["description"].capitalize()

            c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
            c1.write(date)
            c2.write(description)
            c3.write(f"{min_temp:.1f} °C")
            c4.write(f"{max_temp:.1f} °C")
            st.divider()

    except Exception as e:
        st.error("Error in displaying weekly forecast: " + str(e))


# -------------------------
# Main app
# -------------------------
def main():
    # Sidebar
    try:
        st.sidebar.image("Logo.jpg", width=120)
    except Exception:
        pass

    st.sidebar.title("Weather Forecasting")
    city = st.sidebar.text_input("Enter the city name", "London")

    # Keys (IMPORTANT: use secrets/env, not hardcoded)
    weather_api_key = get_secret("OPENWEATHER_API_KEY")
    openai_api_key = get_secret("OPENAI_API_KEY")  # optional, not used

    if not weather_api_key:
        st.sidebar.error("OPENWEATHER_API_KEY missing. Add it in Streamlit Secrets or .env")
        st.stop()

    # Button
    submit = st.sidebar.button("Get Weather")

    if submit:
        st.title("Weather Updates for " + city)

        with st.spinner("Fetching weather data..."):
            weather_data = get_weather_data(city, weather_api_key)

        cod = weather_data.get("cod")
        if cod == 401 or cod == "401":
            st.error("Invalid OpenWeather API key (401). Check your Streamlit Secrets.")
            st.stop()

        if cod == 404 or cod == "404":
            st.error("City not found or an error occurred!")
            st.stop()

        if "main" not in weather_data:
            st.error(f"Unexpected response: {weather_data}")
            st.stop()

        # Main metrics (same style as your old code)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{weather_data['main']['temp'] - 273.15:.2f} °C")
            st.metric("Humidity", f"{weather_data['main']['humidity']}%")
        with col2:
            st.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")
            st.metric("Pressure", f"{weather_data['main']['pressure']} hPa")

        lat = weather_data["coord"]["lat"]
        lon = weather_data["coord"]["lon"]

        st.write(generate_weather_description(weather_data))

        # Forecast
        with st.spinner("Fetching weekly forecast..."):
            forecast_data = get_weekly_forecast(weather_api_key, lat, lon)

        forecast_cod = forecast_data.get("cod")
        if forecast_cod == "401" or forecast_cod == 401:
            st.error("Invalid OpenWeather API key for forecast (401).")
            st.stop()

        if "list" in forecast_data:
            display_weekly_forecast(forecast_data)
        else:
            st.error("Error fetching weekly forecast data!")


if __name__ == "__main__":
    main()

import os
from dotenv import load_dotenv

import streamlit as st
import requests
from datetime import datetime

# Load environment variables from .env (LOCAL only)
# On Streamlit Cloud, you should use st.secrets instead (handled below)
load_dotenv()


# ---------- Helpers to read keys (works locally + Streamlit Cloud) ----------
def get_secret(name: str):
    # Local: .env -> os.getenv
    # Cloud: Streamlit Secrets -> st.secrets
    return os.getenv(name) or st.secrets.get(name, None)


# ---------- OpenWeather API ----------
def get_weather_data(city, weather_api_key):
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={weather_api_key}&q={city}"
    response = requests.get(complete_url, timeout=15)
    return response.json()


def get_weekly_forecast(weather_api_key, lat, lon):
    base_url = "https://api.openweathermap.org/data/2.5/forecast?"
    complete_url = f"{base_url}lat={lat}&lon={lon}&appid={weather_api_key}"
    response = requests.get(complete_url, timeout=15)
    return response.json()


# ---------- Weather description (mock for now, no OpenAI call yet) ----------
def generate_weather_description(data):
    temperature = data["main"]["temp"] - 273.15
    description = data["weather"][0]["description"]
    return (
        f"The current weather in your city is: {description} "
        f"with a temperature of {temperature:.1f} °C."
    )


# ---------- UI: Display forecast ----------
def display_weekly_forecast(data):
    try:
        if "list" not in data:
            st.error("No forecast data available!")
            return

        st.write("### Weekly Weather Forecast")
        displayed_dates = set()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("", "Day")
        c2.metric("", "Desc")
        c3.metric("", "Min_temp")
        c4.metric("", "Max_temp")

        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%A, %B %d")

            # show one row per date
            if date in displayed_dates:
                continue
            displayed_dates.add(date)

            min_temp = item["main"]["temp_min"] - 273.15
            max_temp = item["main"]["temp_max"] - 273.15
            description = item["weather"][0]["description"]

            with c1:
                st.write(date)
            with c2:
                st.write(description.capitalize())
            with c3:
                st.write(f"{min_temp:.1f} °C")
            with c4:
                st.write(f"{max_temp:.1f} °C")

    except Exception as e:
        st.error("Error in displaying weekly forecast: " + str(e))


# ---------- Main App ----------
def main():
    st.set_page_config(page_title="Weather Forecasting App", layout="wide")

    # Sidebar
    try:
        st.sidebar.image("Logo.jpg", width=120)
    except Exception:
        pass

    st.sidebar.title("Weather Forecasting")
    city = st.sidebar.text_input("Enter the city name", "London")

    # Read keys (Local .env OR Streamlit Secrets)
    weather_api_key = get_secret("OPENWEATHER_API_KEY")

    # OpenAI key is OPTIONAL for now (since we are not calling OpenAI yet)
    # openai_api_key = get_secret("OPENAI_API_KEY")

    if not weather_api_key:
        st.sidebar.error(
            "OPENWEATHER_API_KEY missing.\n\n"
            "✅ Local: create a .env file with OPENWEATHER_API_KEY=...\n"
            "✅ Streamlit Cloud: add it in App Settings → Secrets."
        )
        st.stop()

    # Button
    submit = st.sidebar.button("Get Weather")

    if submit:
        st.title(f"Weather Updates for {city}")

        with st.spinner("Fetching weather data..."):
            weather_data = get_weather_data(city, weather_api_key)

        cod = weather_data.get("cod")

        if cod == 404 or cod == "404":
            st.error("City not found or an error occurred!")
            return

        # Show current weather
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{weather_data['main']['temp'] - 273.15:.2f} °C")
            st.metric("Humidity", f"{weather_data['main']['humidity']}%")
        with col2:
            st.metric("Pressure", f"{weather_data['main']['pressure']} hPa")
            st.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")

        # Friendly description (mock)
        st.write(generate_weather_description(weather_data))

        # Weekly forecast
        lat = weather_data["coord"]["lat"]
        lon = weather_data["coord"]["lon"]

        with st.spinner("Fetching weekly forecast..."):
            forecast_data = get_weekly_forecast(weather_api_key, lat, lon)

        forecast_cod = forecast_data.get("cod")
        if forecast_cod == 404 or forecast_cod == "404":
            st.error("Error fetching weekly forecast data!")
            return

        display_weekly_forecast(forecast_data)


if __name__ == "__main__":
    main()

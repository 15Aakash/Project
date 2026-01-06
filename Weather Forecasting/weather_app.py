import os
from dotenv import load_dotenv

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Load environment variables from .env (local only)
load_dotenv()

# ---------------------- API FUNCTIONS ---------------------- #

def get_weather_data(city, weather_api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?appid={weather_api_key}&q={city}"
    return requests.get(url).json()

def get_weekly_forecast(weather_api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={weather_api_key}"
    return requests.get(url).json()

def generate_weather_description(data):
    temperature = data["main"]["temp"] - 273.15
    description = data["weather"][0]["description"]
    return f"The current weather in your city is: {description} with a temperature of {temperature:.1f} °C."


# ---------------------- GRAPH ---------------------- #
# OpenWeather "forecast" endpoint gives data in 3-hour intervals.
# We pick ONE point per day and plot 7 days.

def display_temperature_graph(forecast_data, days=7):
    if "list" not in forecast_data:
        st.error("No forecast data available for graph.")
        return

    points = []
    seen_dates = set()

    for item in forecast_data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        date_key = dt.date()

        if date_key not in seen_dates:
            seen_dates.add(date_key)
            points.append({
                "Date": dt.strftime("%a, %b %d"),
                "Temp (°C)": round(item["main"]["temp"] - 273.15, 2)
            })

        if len(points) == days:
            break

    df = pd.DataFrame(points)
    st.subheader(f"Temperature Trend (Next {days} Days)")
    st.line_chart(df.set_index("Date"))


# ---------------------- OLD STYLE TABLE (YOUR OUTPUT) ---------------------- #

def display_weekly_forecast(data, days=7):
    try:
        if "list" not in data:
            st.error("No forecast data available!")
            return

        st.write("=================================================================================")
        st.write("### Weekly Weather Forecast")

        displayed_dates = set()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("", "Day")
        with c2:
            st.metric("", "Desc")
        with c3:
            st.metric("", "Min Temp")
        with c4:
            st.metric("", "Max Temp")

        count = 0
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%A, %B %d")

            if date not in displayed_dates:
                displayed_dates.add(date)

                min_temp = item["main"]["temp_min"] - 273.15
                max_temp = item["main"]["temp_max"] - 273.15
                desc = item["weather"][0]["description"]

                with c1:
                    st.write(date)
                with c2:
                    st.write(desc.capitalize())
                with c3:
                    st.write(f"{min_temp:.1f} °C")
                with c4:
                    st.write(f"{max_temp:.1f} °C")

                count += 1
                if count == days:
                    break

    except Exception as e:
        st.error("Error in displaying weekly forecast: " + str(e))


# ---------------------- MAIN APP ---------------------- #

def main():
    st.set_page_config(page_title="Weather Forecasting", layout="wide")

    # Sidebar logo
    try:
        st.sidebar.image("Logo.jpg", width=120)
    except Exception:
        pass

    st.sidebar.title("Weather Forecasting with LLM")
    city = st.sidebar.text_input("Enter the city name", "London")

    # ✅ API key from .env OR Streamlit Secrets
    weather_api_key = os.getenv("OPENWEATHER_API_KEY") or st.secrets.get("OPENWEATHER_API_KEY")

    if not weather_api_key:
        st.sidebar.error("OPENWEATHER_API_KEY missing. Add it to .env (local) or Secrets (cloud).")
        st.stop()

    submit = st.sidebar.button("Get Weather")

    if submit:
        st.title("Weather Updates for " + city)

        with st.spinner("Fetching weather data..."):
            weather_data = get_weather_data(city, weather_api_key)

        if str(weather_data.get("cod")) != "200":
            st.error(f"Error fetching weather: {weather_data.get('message', 'Unknown error')}")
            st.stop()

        # Metrics (same style as your old output)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{weather_data['main']['temp'] - 273.15:.2f} °C")
            st.metric("Humidity", f"{weather_data['main']['humidity']}%")
        with col2:
            st.metric("Pressure", f"{weather_data['main']['pressure']} hPa")
            st.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")

        st.write(generate_weather_description(weather_data))

        lat = weather_data["coord"]["lat"]
        lon = weather_data["coord"]["lon"]

        forecast_data = get_weekly_forecast(weather_api_key, lat, lon)

        # ✅ GRAPH first
        display_temperature_graph(forecast_data, days=7)

        # ✅ THEN your old weekly layout
        display_weekly_forecast(forecast_data, days=7)


if __name__ == "__main__":
    main()

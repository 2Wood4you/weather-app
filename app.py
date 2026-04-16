import streamlit as st
import requests
import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
from timezonefinder import TimezoneFinder
from datetime import datetime
from zoneinfo import ZoneInfo

base_url = "https://api.open-meteo.com/v1/forecast"
latitude = 0
longitude = 0
result = None
timezone = ""

@st.cache_data
def get_info(city_name):
    geolocator = Nominatim(user_agent="should-i-go-outside", timeout=10)
    try:
        location = geolocator.geocode(city_name)
    except GeocoderUnavailable:
        st.write("Geocoding service unavailable ❌ Try again later")
        return None

    if location is None:
        st.write("City not found ❌")
        return

    l_latitude = location.latitude
    l_longitude = location.longitude

    return l_latitude, l_longitude


def get_forecast():
    url = f"{base_url}?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,rain,wind_speed_10m&timezone={timezone}&forecast_days=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.write(f"Failed to retrieve data {response.status_code}")


tf = TimezoneFinder()

st.title("Should I go outside?")

userCity = st.text_area("Enter your city:", key="city", height=1)


if st.button("Check Weather"):
    placeholder = st.empty()
    placeholder.write("Checking...")
    # st.write("Checking...")
    result = get_info(userCity)

if result:
    latitude, longitude = result

    timezone = tf.timezone_at(lng=longitude, lat=latitude)
    time_index = datetime.now(ZoneInfo(timezone)).hour

    forecast = get_forecast()



    if forecast:
        placeholder.empty()

        temp = forecast['hourly']['temperature_2m'][time_index]
        rain = forecast['hourly']['rain'][time_index]
        wind = forecast['hourly']['wind_speed_10m'][time_index]

        st.write(f"\nTemperature: {temp}°C")
        st.write(f"Rain: {rain} mm")
        st.write(f"Wind Speed: {wind} km/h")

        bad_weather = False

        if rain > 2:
            bad_weather = True

        if wind > 25:
            bad_weather = True

        if temp < 5:
            bad_weather = True


        st.write("\n")

        if bad_weather:
            st.write("You'd better stay inside!")
        else:
            st.write("The weather's nice — go outside!")

        st.write("\n")

        if temp > 30:
            st.write("Warning: It's too hot!")

        if rain == 0 and temp > 15:
            st.write("Perfect for sports!")

        if temp < 10 and wind > 20:
            st.write("It's unpleasant outside!")
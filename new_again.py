import requests
import datetime
import folium

# === Function to get weather data ===
def get_weather(city, api_key):
    try:
        api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(api_url)
        response.raise_for_status()
        owm_response_json = response.json()

        if "main" in owm_response_json and "weather" in owm_response_json and "coord" in owm_response_json:
            temp_celsius = owm_response_json["main"]["temp"] - 273.15
            humidity = owm_response_json["main"]["humidity"]
            condition = owm_response_json["weather"][0]["description"].title()
            lat = owm_response_json["coord"]["lat"]
            lon = owm_response_json["coord"]["lon"]

            sunset_utc = datetime.datetime.fromtimestamp(owm_response_json["sys"]["sunset"])
            sunset_local = sunset_utc + datetime.timedelta(seconds=owm_response_json["timezone"])

            return {
                "city": city,
                "temp_c": round(temp_celsius, 2),
                "humidity": humidity,
                "condition": condition,
                "sunset_local": sunset_local.strftime("%Y-%m-%d %H:%M:%S"),
                "lat": lat,
                "lon": lon
            }
        else:
            print(f"Unexpected API format for {city}: {owm_response_json}")
            return None

    except Exception as err:
        print(f"Error for {city}: {err}")
        return None


# === Main Script ===
if __name__ == "__main__":
    api_key = "62eac246cacb020df0cdee7bbfc24994"
    cities = ["London", "New York", "Dhaka", "Tokyo", "Sydney"]

    # Initialize map
    weather_map = folium.Map(location=[20, 0], zoom_start=2)

    for city in cities:
        data = get_weather(city, api_key)
        if data:
            popup_text = (f"<b>{data['city']}</b><br>"
                          f"🌡 Temp: {data['temp_c']} °C<br>"
                          f"💧 Humidity: {data['humidity']}%<br>"
                          f"☁ Condition: {data['condition']}<br>"
                          f"🌅 Sunset: {data['sunset_local']}")
            
            folium.Marker(
                location=[data['lat'], data['lon']],
                popup=popup_text,
                icon=folium.Icon(color="blue", icon="cloud")
            ).add_to(weather_map)

    # Save HTML file
    output_file = "weather_map.html"
    weather_map.save(output_file)
    print(f"Weather map saved as {output_file}")

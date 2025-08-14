from flask import Flask, render_template_string
import requests
import datetime
import folium

app = Flask(__name__)

API_KEY = "62eac246cacb020df0cdee7bbfc24994"
CITIES = ["London", "New York", "Dhaka", "Tokyo", "Sydney"]

def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()

        temp_c = data["main"]["temp"] - 273.15
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"].title()
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        sunset_utc = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        sunset_local = sunset_utc + datetime.timedelta(seconds=data["timezone"])

        return {
            "city": city,
            "temp_c": round(temp_c, 2),
            "humidity": humidity,
            "condition": condition,
            "sunset_local": sunset_local.strftime("%Y-%m-%d %H:%M:%S"),
            "lat": lat,
            "lon": lon
        }
    except:
        return None

@app.route("/")
def index():
    # Create map
    weather_map = folium.Map(location=[20, 0], zoom_start=2)
    for city in CITIES:
        data = get_weather(city)
        if data:
            popup_text = f"<b>{data['city']}</b><br>Temp: {data['temp_c']} °C<br>Humidity: {data['humidity']}%<br>Condition: {data['condition']}<br>Sunset: {data['sunset_local']}"
            folium.Marker([data['lat'], data['lon']], popup=popup_text).add_to(weather_map)
    
    # Render map as HTML
    return render_template_string(weather_map._repr_html_())

if __name__ == "__main__":
    app.run(debug=True)

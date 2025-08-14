from flask import Flask, render_template_string
import requests
import datetime
import folium
import os  # For Railway port handling

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
        temp_f = temp_c * 9/5 + 32  # Compute Fahrenheit
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"].title()
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        sunset_utc = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        sunset_local = sunset_utc + datetime.timedelta(seconds=data["timezone"])

        return {
            "city": city,
            "temp_c": round(temp_c, 2),
            "temp_f": round(temp_f, 2),
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
    temps_c = []  # For average temperature computation

    for city in CITIES:
        data = get_weather(city)
        if data:
            temps_c.append(data["temp_c"])
            popup_text = (
                f"🌆 <b>{data['city']}</b><br>"
                f"🌡 Temp: {data['temp_c']} °C / {data['temp_f']} °F<br>"
                f"💧 Humidity: {data['humidity']}%<br>"
                f"☁ Condition: {data['condition']}<br>"
                f"🌅 Sunset: {data['sunset_local']}"
            )
            folium.Marker([data['lat'], data['lon']], popup=popup_text).add_to(weather_map)

    # Compute average temperature
    if temps_c:
        avg_c = round(sum(temps_c) / len(temps_c), 2)
        avg_f = round(avg_c * 9/5 + 32, 2)
        folium.Marker(
            [20, 0],  # Central location for average temp
            popup=f"🌡 <b>Average Temp:</b> {avg_c} °C / {avg_f} °F",
            icon=folium.Icon(color='green')
        ).add_to(weather_map)

    # Render map as HTML with UTF-8 encoding for emojis
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Weather Map</title>
    </head>
    <body>
        {weather_map._repr_html_()}
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway port
    app.run(host="0.0.0.0", port=port)

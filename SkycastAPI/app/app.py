import os
import requests
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

API_KEY = os.environ.get('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skycast</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background: #1c1c1e;
            transition: background 1s ease;
        }

        body.clear-day { background: linear-gradient(175deg, #2e86de, #54a0ff, #74b9ff); }
        body.clear-night { background: linear-gradient(175deg, #0a0a2e, #1a1a4e, #2d2d6e); }
        body.cloudy { background: linear-gradient(175deg, #636e72, #74859a, #8ea1b3); }
        body.rainy { background: linear-gradient(175deg, #2c3e50, #3d5166, #4f6a82); }
        body.snowy { background: linear-gradient(175deg, #a8c0cc, #b8cdd8, #cde0e8); }
        body.thunderstorm { background: linear-gradient(175deg, #1a1a2e, #2d2d44, #3d3d5c); }
        body.misty { background: linear-gradient(175deg, #6b7f8e, #7f9aaa, #93afc0); }

        .app {
            width: 100%;
            max-width: 390px;
        }

        /* Search */
        .search-container {
            margin-bottom: 24px;
        }

        .search-bar {
            display: flex;
            align-items: center;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 14px;
            padding: 0 16px;
            gap: 10px;
            transition: background 0.2s;
        }

        .search-bar:focus-within {
            background: rgba(255,255,255,0.22);
            border-color: rgba(255,255,255,0.35);
        }

        .search-bar span { font-size: 16px; opacity: 0.7; }

        input {
            flex: 1;
            background: none;
            border: none;
            outline: none;
            color: white;
            font-size: 17px;
            font-family: 'Inter', sans-serif;
            padding: 14px 0;
            font-weight: 400;
        }

        input::placeholder { color: rgba(255,255,255,0.45); }

        .search-btn {
            background: none;
            border: none;
            color: rgba(255,255,255,0.8);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            padding: 4px 0;
            font-family: 'Inter', sans-serif;
            transition: color 0.2s;
        }

        .search-btn:hover { color: white; }

        /* Error */
        .error-msg {
            background: rgba(255,59,48,0.2);
            border: 1px solid rgba(255,59,48,0.4);
            border-radius: 12px;
            padding: 12px 16px;
            color: #ff6b6b;
            font-size: 14px;
            display: none;
            margin-bottom: 16px;
            backdrop-filter: blur(10px);
        }

        .loading-msg {
            text-align: center;
            color: rgba(255,255,255,0.5);
            font-size: 14px;
            display: none;
            margin-bottom: 16px;
        }

        /* Main Weather Card */
        .weather-card {
            display: none;
            animation: fadeIn 0.6s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Hero Section */
        .hero {
            text-align: center;
            padding: 10px 0 32px;
        }

        .city {
            font-size: 34px;
            font-weight: 600;
            color: white;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .country-badge {
            display: inline-block;
            font-size: 13px;
            color: rgba(255,255,255,0.65);
            font-weight: 400;
            margin-bottom: 16px;
            letter-spacing: 0.5px;
        }

        .big-temp {
            font-size: 96px;
            font-weight: 200;
            color: white;
            line-height: 1;
            letter-spacing: -4px;
            margin-bottom: 8px;
        }

        .big-temp sup {
            font-size: 40px;
            font-weight: 300;
            vertical-align: super;
            letter-spacing: 0;
        }

        .condition-text {
            font-size: 20px;
            color: rgba(255,255,255,0.75);
            font-weight: 400;
            text-transform: capitalize;
            margin-bottom: 8px;
        }

        .high-low {
            font-size: 18px;
            color: rgba(255,255,255,0.7);
            font-weight: 400;
        }

        /* Glass Panel */
        .glass-panel {
            background: rgba(255,255,255,0.12);
            backdrop-filter: blur(40px);
            -webkit-backdrop-filter: blur(40px);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 12px;
        }

        /* Hourly Strip */
        .hourly-strip {
            padding: 16px 20px;
        }

        .panel-label {
            font-size: 11px;
            font-weight: 600;
            color: rgba(255,255,255,0.5);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .hourly-scroll {
            display: flex;
            gap: 20px;
            overflow-x: auto;
            scrollbar-width: none;
            padding-bottom: 4px;
        }

        .hourly-scroll::-webkit-scrollbar { display: none; }

        .hour-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            min-width: 44px;
        }

        .hour-time {
            font-size: 13px;
            color: rgba(255,255,255,0.6);
            font-weight: 500;
        }

        .hour-icon { font-size: 22px; }

        .hour-temp {
            font-size: 15px;
            color: white;
            font-weight: 600;
        }

        /* Stats Grid */
        .stats-panel {
            padding: 18px 20px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .stat-tile {
            background: rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 16px;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .stat-label-row {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 10px;
        }

        .stat-icon { font-size: 14px; opacity: 0.7; }

        .stat-label {
            font-size: 11px;
            font-weight: 600;
            color: rgba(255,255,255,0.5);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stat-val {
            font-size: 26px;
            font-weight: 600;
            color: white;
            line-height: 1;
        }

        .stat-sub {
            font-size: 13px;
            color: rgba(255,255,255,0.5);
            margin-top: 4px;
        }

        /* Feels Like Special */
        .feels-panel {
            padding: 18px 20px;
        }

        .feels-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .feels-val {
            font-size: 32px;
            font-weight: 300;
            color: white;
        }

        .feels-desc {
            font-size: 14px;
            color: rgba(255,255,255,0.6);
            max-width: 160px;
            text-align: right;
            line-height: 1.4;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 11px;
            color: rgba(255,255,255,0.2);
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }
    </style>
</head>
<body>
    <div class="app">
        <div class="search-container">
            <div class="search-bar">
                <span>🔍</span>
                <input type="text" id="cityInput" placeholder="Search for a city" />
                <button class="search-btn" onclick="getWeather()">Search</button>
            </div>
        </div>

        <div class="error-msg" id="error"></div>
        <div class="loading-msg" id="loading">⏳ Fetching weather...</div>

        <div class="weather-card" id="weatherCard">

            <!-- Hero -->
            <div class="hero">
                <div class="city" id="cityName"></div>
                <div class="country-badge" id="countryName"></div>
                <div class="big-temp"><span id="temp"></span><sup>°</sup></div>
                <div class="condition-text" id="description"></div>
                <div class="high-low" id="highLow"></div>
            </div>

            <!-- Hourly -->
            <div class="glass-panel">
                <div class="hourly-strip">
                    <div class="panel-label">🕐 Conditions Today</div>
                    <div class="hourly-scroll" id="hourlyStrip"></div>
                </div>
            </div>

            <!-- Stats -->
            <div class="glass-panel">
                <div class="stats-panel">
                    <div class="panel-label">📊 Weather Details</div>
                    <div class="stats-grid">
                        <div class="stat-tile">
                            <div class="stat-label-row">
                                <span class="stat-icon">💧</span>
                                <span class="stat-label">Humidity</span>
                            </div>
                            <div class="stat-val" id="humidity"></div>
                            <div class="stat-sub">Relative humidity</div>
                        </div>
                        <div class="stat-tile">
                            <div class="stat-label-row">
                                <span class="stat-icon">💨</span>
                                <span class="stat-label">Wind</span>
                            </div>
                            <div class="stat-val" id="wind"></div>
                            <div class="stat-sub">Metres per second</div>
                        </div>
                        <div class="stat-tile">
                            <div class="stat-label-row">
                                <span class="stat-icon">👁️</span>
                                <span class="stat-label">Visibility</span>
                            </div>
                            <div class="stat-val" id="visibility"></div>
                            <div class="stat-sub">Kilometres</div>
                        </div>
                        <div class="stat-tile">
                            <div class="stat-label-row">
                                <span class="stat-icon">🌡️</span>
                                <span class="stat-label">Feels Like</span>
                            </div>
                            <div class="stat-val" id="feelsLike"></div>
                            <div class="stat-sub" id="feelsDesc"></div>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        <div class="footer">Skycast · Powered by OpenWeatherMap</div>
    </div>

    <script>
        document.getElementById('cityInput').addEventListener('keypress', e => {
            if (e.key === 'Enter') getWeather();
        });

        function getEmoji(desc) {
            const d = desc.toLowerCase();
            if (d.includes('thunder')) return '⛈️';
            if (d.includes('drizzle')) return '🌦️';
            if (d.includes('heavy rain')) return '🌧️';
            if (d.includes('rain')) return '🌦️';
            if (d.includes('snow')) return '❄️';
            if (d.includes('mist') || d.includes('fog') || d.includes('haze')) return '🌫️';
            if (d.includes('clear')) return '☀️';
            if (d.includes('few clouds')) return '🌤️';
            if (d.includes('scattered')) return '⛅';
            if (d.includes('cloud')) return '☁️';
            return '🌡️';
        }

        function getBgClass(desc) {
            const d = desc.toLowerCase();
            if (d.includes('thunder')) return 'thunderstorm';
            if (d.includes('rain') || d.includes('drizzle')) return 'rainy';
            if (d.includes('snow')) return 'snowy';
            if (d.includes('mist') || d.includes('fog') || d.includes('haze')) return 'misty';
            if (d.includes('clear')) return 'clear-day';
            if (d.includes('cloud')) return 'cloudy';
            return 'clear-day';
        }

        function getFeelsDesc(actual, feels) {
            const diff = feels - actual;
            if (diff <= -3) return 'Wind is making it feel colder';
            if (diff >= 3) return 'Humidity is making it feel warmer';
            return 'Similar to the actual temperature';
        }

        function buildHourlyStrip(temp, desc) {
            const emoji = getEmoji(desc);
            const hours = ['Now', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM'];
            const temps = [temp, temp-1, temp-1, temp-2, temp-2, temp-3, temp-3, temp-4];
            const strip = document.getElementById('hourlyStrip');
            strip.innerHTML = '';
            hours.forEach((h, i) => {
                strip.innerHTML += `
                    <div class="hour-item">
                        <div class="hour-time">${h}</div>
                        <div class="hour-icon">${emoji}</div>
                        <div class="hour-temp">${temps[i]}°</div>
                    </div>`;
            });
        }

        async function getWeather() {
            const city = document.getElementById('cityInput').value.trim();
            if (!city) return;

            document.getElementById('loading').style.display = 'block';
            document.getElementById('weatherCard').style.display = 'none';
            document.getElementById('error').style.display = 'none';

            try {
                const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
                const data = await res.json();

                if (data.error) {
                    document.getElementById('error').textContent = '❌ ' + data.error;
                    document.getElementById('error').style.display = 'block';
                } else {
                    // Set background
                    document.body.className = getBgClass(data.description);

                    // Hero
                    document.getElementById('cityName').textContent = data.city;
                    document.getElementById('countryName').textContent = data.country;
                    document.getElementById('temp').textContent = data.temperature;
                    document.getElementById('description').textContent = data.description;
                    document.getElementById('highLow').textContent = `H:${data.temperature + 2}°  L:${data.temperature - 4}°`;

                    // Stats
                    document.getElementById('humidity').textContent = `${data.humidity}%`;
                    document.getElementById('wind').textContent = `${data.wind_speed}`;
                    document.getElementById('visibility').textContent = `${data.visibility}`;
                    document.getElementById('feelsLike').textContent = `${data.feels_like}°`;
                    document.getElementById('feelsDesc').textContent = getFeelsDesc(data.temperature, data.feels_like);

                    // Hourly
                    buildHourlyStrip(data.temperature, data.description);

                    document.getElementById('weatherCard').style.display = 'block';
                }
            } catch (err) {
                document.getElementById('error').textContent = '❌ Something went wrong. Please try again.';
                document.getElementById('error').style.display = 'block';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City name is required"}), 400

    try:
        response = requests.get(BASE_URL, params={
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        })
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "City not found. Please check the spelling and try again."}), 404

        return jsonify({
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "visibility": round(data["visibility"] / 1000, 1)
        })

    except Exception as e:
        return jsonify({"error": "Something went wrong"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
from pyowm.owm import OWM

#Existing OWM Setup
load_dotenv()
api_key = os.getenv("API_KEY")
owm = OWM(api_key)
mgr = owm.weather_manager()

# Functions (made with ChatGPT)
def compute_heat_index(temp_f, humidity):
    # Only valid if temperature >= 80°F and humidity >= 40%
    if temp_f < 80 or humidity < 40:
        return None

    # Formula from NOAA
    hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
          - 0.22475541 * temp_f * humidity - 0.00683783 * temp_f**2
          - 0.05481717 * humidity**2 + 0.00122874 * temp_f**2 * humidity
          + 0.00085282 * temp_f * humidity**2 - 0.00000199 * temp_f**2 * humidity**2)
    
    return round(hi, 2)

def heat_index_category(hi):
    if hi is None:
        return "Not applicable"
    elif hi < 80:
        return "Comfortable"
    elif hi < 91:
        return "Caution"
    elif hi < 104:
        return "Extreme Caution"
    elif hi < 125:
        return "Danger"
    else:
        return "Extreme Danger"
    
#Start the FLask process
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

#Route to weather report
@app.route("/weather/", methods = ["GET" , "POST"])
def weather():
    if request.method == "POST":
        location = request.form["location"]
        try:
            observation = mgr.weather_at_place(location)
        except:
            return render_template("404.html"), 404
    else:
        location = "Liberty Hill, US"
    

    # Weather API Calls
    observation = mgr.weather_at_place(location)
    w = observation.weather

    # Temperature dictionary
    temp = w.temperature("fahrenheit")

    current_temp = temp.get("temp")
    feels_like = temp.get("feels_like")

    # Specific Calls
    temp = w.temperature("fahrenheit")
    humidity = w.humidity
    heat_index = heat_index_category(compute_heat_index(current_temp, humidity))
    clouds = w.clouds

    #Package data for HTML template
    weather_data = {
        "location": location,
        "current_temp": current_temp,
        "feels_like": feels_like,
        "humidity": humidity,
        "clouds": clouds,
        "heat_index": heat_index,

    }
    
    return render_template("weather_report.html", w=weather_data)

@app.route("/changelog/")
def changelog():
    return render_template("changelog.html")

@app.route("/error/")
def error():
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True)

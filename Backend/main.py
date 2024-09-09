import openmeteo_requests
from retry_requests import retry
import requests_cache
import pandas as pd
from flask import Flask, render_template, request
import os

app = Flask(__name__, template_folder=os.path.abspath('../Webpages'), static_folder=os.path.abspath('../Webpages/static'))

# This will store submitted data for demonstration purposes
submitted_data = []

@app.route("/")
def home():
    return render_template("home.html")


def prediction_call(locations):
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": locations[0],
        "longitude": locations[1],
        "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum"],
        "Timezone": "auto"
    }
    responses = openmeteo.weather_api(url, params=params)
    return responses

# Function to process the prediction results (from the notebook)
def extract_process(responses):
    response = responses[0]
    daily_data = response.Daily()

    temp_min = daily_data.Variables(0).ValuesAsNumpy()
    temp_max = daily_data.Variables(1).ValuesAsNumpy()
    rain_sum = daily_data.Variables(2).ValuesAsNumpy()

    daily_index = pd.date_range(
        start=pd.to_datetime(daily_data.Time(), unit="s"),
        end=pd.to_datetime(daily_data.TimeEnd(), unit="s"),
        freq=pd.Timedelta(seconds=daily_data.Interval()),
        inclusive="left"
    )

    daily_df = pd.DataFrame({
        "Datetime": daily_index,
        "Minimum Temperature": temp_min,
        "Maximum Temperature": temp_max,
        "Rain": rain_sum
    })
    return daily_df


@app.route('/submit', methods=['POST'])
def submit():
   # Get the location and selected variable from the form
    locations = request.form.get('location')
    reponse = prediction_call(locations)
    result = extract_process(reponse)

    # Render the table in an HTML template
    return render_template('table.html', location=locations, table=result.to_html(classes='data'))




@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)

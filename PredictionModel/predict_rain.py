from random import randint
import sys
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
sys.path.append('../Backend/Conversions')
import convertt

def predict_rain(suburb):
    """
    Predict the probability of raining tomorrow for one location
    
    Input:
        id: clusterid (location)
    Output:
        prob_rain: probability of rain tomorrow on the selected location (cluster_id)
    """

    return randint(0,100)

def predict_rains_hourly(suburblist):
    """
    Predict the probability of raining today + tomorrow for multiple locations

    Input:
        suburblist: list of suburbs. e.g. ['Melbourne', 'Clayton'] or ['Melbourne'] for single location
    Output:
        prob_dict: dictionary containing clusterid and the probablity of raining tmr for that id
    """
    suburblist_valid = []
    ids = []
    latitude = []
    longitude = []
    for i in range(len(suburblist)):
        r = convertt.suburb_info([suburblist[i]])
        if r:
            suburblist_valid.append(suburblist[i])
            t = r[0] # Tuple
            ids.append(t[0])
            latitude.append(t[1])
            longitude.append(t[2])

    suburb_cluster = pd.DataFrame({'suburb':suburblist_valid, 'clusterid':ids,
                               'latitude':latitude, 'longitude':longitude})
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": suburb_cluster.latitude,
        "longitude": suburb_cluster.longitude,
        "hourly": "precipitation_probability",
        "forecast_days": 2
    }
    responses = openmeteo.weather_api(url, params=params)

    df = pd.DataFrame({"suburb":[], "datetime":[], "rain_probability":[]})
    for i in range(len(responses)):
        response = responses[i]
        hourly = response.Hourly()
        hourly_precipitation_probability = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {
            "suburb": suburb_cluster.iloc[i]['suburb'],
            "datetime": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["rain_probability"] = hourly_precipitation_probability
        hourly_dataframe = pd.DataFrame(data = hourly_data)

        df = pd.concat((df, hourly_dataframe), ignore_index=True)

    return df
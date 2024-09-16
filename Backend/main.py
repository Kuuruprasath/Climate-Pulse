import openmeteo_requests
from retry_requests import retry
import requests_cache
import pandas as pd
from flask import Flask, render_template, request
import os

import plotly.express as px
from Conversions import convertt
import psycopg2

app = Flask(__name__, template_folder=os.path.abspath('../Webpages'), static_folder=os.path.abspath('../Webpages/static'))

# This will store submitted data for demonstration purposes
submitted_data = []

@app.route("/home", methods=['GET'])
def home():
    return render_template("Home page/index.html")

@app.route('/temperature-wind')
def temperature_wind():
    return render_template('Home page/temperature-wind.html')

@app.route('/precipitation')
def precipitation():
    return render_template('Home page/precipitation.html')

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


@app.route('/predict_model_API', methods=['POST'])
def submit():
   # Get the location and selected variable from the form
    locations = request.form.get('location')
    reponse = prediction_call(locations)
    result = extract_process(reponse)

    # Render the table in an HTML template
    return render_template('table.html', location=locations, table=result.to_html(classes='data'))


def get_dataset(suburbList):
    import pandas as pd
    clusterid,datetime,temperature,rainfall = convertt.suburb_to_var(suburbList)
    dataset = {
    'clusterid' : clusterid,
    'datetime': datetime,
    'temperature': temperature,
    'rainfall': rainfall
    }
    dataset = pd.DataFrame(dataset)
    return dataset

def lineChart(dataset,variable,startDate,endDate,period,suburbs):


    dataset["datetime"] = pd.to_datetime(dataset["datetime"])
    dataset['datetime'] = dataset['datetime'].dt.tz_localize('UTC').dt.tz_convert('UTC')
    daterange = pd.date_range(startDate, endDate, freq=period)

    filtered_dataset = dataset[dataset["datetime"].isin(daterange)]
    fig = px.line(filtered_dataset, y=variable,x = "datetime",color= 'clusterid')

    unique_values = filtered_dataset['clusterid'].unique()
    newnames = {int(unique_values[i]): suburbs[i] for i in range(len(unique_values))}

    fig.for_each_trace(lambda t: t.update(name=newnames.get(int(t.name), t.name),
                                      legendgroup=newnames.get(int(t.name), t.name),
                                      hovertemplate=t.hovertemplate.replace(t.name, newnames.get(int(t.name), t.name))
                                     ))
    
    fig.update_layout(plot_bgcolor='white')
    
    return fig

def barChart(dataset,variable,startDate,endDate,period,suburbs):


    dataset["datetime"] = pd.to_datetime(dataset["datetime"])
    dataset['datetime'] = dataset['datetime'].dt.tz_localize('UTC').dt.tz_convert('UTC')
    daterange = pd.date_range(startDate, endDate, freq=period)

    filtered_dataset = dataset[dataset["datetime"].isin(daterange)]

    fig = px.bar(filtered_dataset, y=variable,x = "datetime",color ='clusterid' )
    fig.update_layout(plot_bgcolor='white')
    return fig

def histogram(dataset,variable,startDate,endDate,period,suburbs):


    dataset["datetime"] = pd.to_datetime(dataset["datetime"])
    dataset['datetime'] = dataset['datetime'].dt.tz_localize('UTC').dt.tz_convert('UTC')

    daterange = pd.date_range(startDate, endDate, freq=period)

    filtered_dataset = dataset[dataset["datetime"].isin(daterange)]

    fig = px.histogram(filtered_dataset,x = variable,nbins=31,color='clusterid')
    unique_values = filtered_dataset['clusterid'].unique()
    newnames = {int(unique_values[i]): suburbs[i] for i in range(len(unique_values))}

    fig.for_each_trace(lambda t: t.update(name=newnames.get(int(t.name), t.name),
                                      legendgroup=newnames.get(int(t.name), t.name),
                                      hovertemplate=t.hovertemplate.replace(t.name, newnames.get(int(t.name), t.name))
                                     ))
    fig.update_layout(plot_bgcolor='white')

    return fig

def areaChart(dataset,variable,startDate,endDate,period,suburbs):


    dataset["datetime"] = pd.to_datetime(dataset["datetime"])
    dataset['datetime'] = dataset['datetime'].dt.tz_localize('UTC').dt.tz_convert('UTC')
    daterange = pd.date_range(startDate, endDate, freq=period)

    filtered_dataset = dataset[dataset["datetime"].isin(daterange)]

    fig = px.area(filtered_dataset,x = "datetime",y = variable,color = 'clusterid')
    unique_values = filtered_dataset['clusterid'].unique()
    newnames = {int(unique_values[i]): suburbs[i] for i in range(len(unique_values))}

    fig.for_each_trace(lambda t: t.update(name=newnames.get(int(t.name), t.name),
                                      legendgroup=newnames.get(int(t.name), t.name),
                                      hovertemplate=t.hovertemplate.replace(t.name, newnames.get(int(t.name), t.name))
                                     ))
    fig.update_layout(plot_bgcolor='white')

    return fig


@app.route('/process', methods=['POST'])
def process():
    start_date = pd.Timestamp(request.form['startDate'], tz='UTC')
    end_date = pd.Timestamp(request.form['endDate'], tz='UTC')
    variable = request.form['variable']
    period = request.form['period']
    chartType = request.form['chartType']
    
    # Suburbs entered as a comma-separated string, split by commas and strip extra spaces
    suburbs = [suburb.strip() for suburb in request.form['suburbs'].split(',')]

    dataset = get_dataset(suburbs)
    
    if chartType == 'lineChart':
        fig = lineChart(dataset,variable,start_date,end_date,period,suburbs)
    elif chartType == 'barChart':
        fig = barChart(dataset,variable,start_date,end_date,period,suburbs)
    elif chartType == 'histogram':
        fig = histogram(dataset,variable,start_date,end_date,period,suburbs)
    elif chartType == 'areaChart':
        fig = areaChart(dataset,variable,start_date,end_date,period,suburbs)
    
    fig_html = fig.to_html(full_html=False)

    # Render the figure in the template
    return render_template('plot.html', fig_html=fig_html)

    # Perform your data processing here
    #return f"Start Date: {start_date}, End Date: {end_date}, Variable: {variable}, Period: {period}, Suburbs: {suburbs}"




@app.route("/contact", methods=['GET'])
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)

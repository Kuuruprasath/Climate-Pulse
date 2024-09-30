from retry_requests import retry
import requests_cache
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import iplot
from Conversions import convertt
import pandas.io.sql as sqlio
import psycopg2
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, template_folder=os.path.abspath('../Webpages'), static_folder=os.path.abspath('../Webpages/static'))
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/temperature')
def temperature():
    return render_template('temperature-wind.html')

@app.route('/precipitation')
def precipitation():
    return render_template('precipitation.html')

@app.route('/about_us')
def about_us():
    return render_template('aboutus.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contactus.html')

@app.route('/analysis')
def analysis():
    return render_template('map_combined.html')

#Analysis function
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

def lineChart(dataset, variable, startDate, endDate, period, suburbs):
    import plotly.express as px
    import pandas as pd

    # Ensure the datetime column is in datetime format
    dataset["datetime"] = pd.to_datetime(dataset["datetime"])

    # Directly convert timezone if the datetime is already tz-aware
    dataset['datetime'] = dataset['datetime'].dt.tz_convert('UTC')
    
    # Create the date range
    daterange = pd.date_range(startDate, endDate, freq=period)

    # Filter the dataset based on the daterange
    filtered_dataset = dataset[dataset["datetime"].isin(daterange)]

    # Create the line chart using Plotly
    fig = px.line(filtered_dataset, y=variable, x="datetime", color='clusterid')

    # Map the unique values to suburb names
    unique_values = filtered_dataset['clusterid'].unique()
    newnames = {int(unique_values[i]): suburbs[i] for i in range(len(unique_values))}

    # Update the trace names for the legend and hover labels
    fig.for_each_trace(lambda t: t.update(name=newnames.get(int(t.name), t.name),
                                          legendgroup=newnames.get(int(t.name), t.name),
                                          hovertemplate=t.hovertemplate.replace(t.name, newnames.get(int(t.name), t.name))
                                         ))
    
    # Update the layout
    fig.update_layout(plot_bgcolor='white')
    
    return fig

def barChart(dataset,variable,startDate,endDate,period,suburbs):


    dataset["datetime"] = pd.to_datetime(dataset["datetime"])
    dataset['datetime'] = dataset['datetime'].dt.tz_convert('UTC')
    daterange = pd.date_range(startDate, endDate, freq=period)

    filtered_dataset = dataset[dataset["datetime"].isin(daterange)]

    fig = px.bar(filtered_dataset, y=variable,x = "datetime",color ='clusterid' )
    fig.update_layout(plot_bgcolor='white')
    return fig

def histogram(dataset,variable,startDate,endDate,period,suburbs):


    dataset["datetime"] = pd.to_datetime(dataset["datetime"])
    dataset['datetime'] = dataset['datetime'].dt.tz_convert('UTC')

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
    dataset['datetime'] = dataset['datetime'].dt.tz_convert('UTC')
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

def pointChart(dataset,variable,startDate,endDate,period, suburbs):

    dataset["datetime"] = pd.to_datetime(dataset["datetime"])
    dataset['datetime'] = dataset['datetime'].dt.tz_convert('UTC')

    daterange = pd.date_range(startDate, endDate, freq=period)

    filtered_dataset = dataset[dataset["datetime"].isin(daterange)]

    #fig = px.scatter(filtered_dataset, y=variable[0],x = variable[1])
    fig = px.scatter(filtered_dataset, y='temperature',x = 'rainfall')
    fig.update_layout(plot_bgcolor='white')
    #fig.show()
    return fig

def line_bar_chart(dataset,variable, startDate, endDate, period, suburbs):
    dataset["datetime"] = pd.to_datetime(dataset["datetime"])
    dataset['datetime'] = dataset['datetime'].dt.tz_convert('UTC')

    daterange = pd.date_range(startDate, endDate, freq=period)
    filtered_dataset = dataset[dataset["datetime"].isin(daterange)]

    trace1 = go.Scatter(
        mode='lines+markers',
        x=filtered_dataset['datetime'],
        y=filtered_dataset['temperature'],
        name="Temperature",
        marker_color='yellow'
    )

    trace2 = go.Bar(
        x=filtered_dataset['datetime'],
        y=filtered_dataset['rainfall'],
        name="Rainfall",
        yaxis='y2',
        marker_color= 'rgb(0,181,226)',
        marker_line_width=1.5,
        marker_line_color='rgb(0,181,226)',
        opacity=0.5
    )

    data = [trace1, trace2]

    layout = go.Layout(
        title_text='Temperature and Rainfall Over Time',
        yaxis=dict(
            title='Temperature',
            side='left'
        ),
        yaxis2=dict(
            title='Rainfall',
            overlaying='y',
            side='right'
        ),
        plot_bgcolor='rgba(0,0,0,0)',

    )

    fig = go.Figure(data=data, layout=layout)
    return fig



@app.route('/process', methods=['POST'])
def process():
    start_date = pd.Timestamp(request.form['startDate'], tz='UTC')
    end_date = pd.Timestamp(request.form['endDate'], tz='UTC')
    variable = request.form['variable']
    period = request.form['period']
    chartType = request.form['chartType']
    
    # Suburbs entered as a comma-separated string, split by commas and strip extra spaces
    suburbs = [suburb.strip() for suburb in request.form['suburbs_1'].split(',')]

    dataset = get_dataset(suburbs)
    
    if chartType == 'lineChart':
        fig = lineChart(dataset,variable,start_date,end_date,period,suburbs)
    elif chartType == 'barChart':
        fig = barChart(dataset,variable,start_date,end_date,period,suburbs)
    elif chartType == 'histogram':
        fig = histogram(dataset,variable,start_date,end_date,period,suburbs)
    elif chartType == 'areaChart':
        fig = areaChart(dataset,variable,start_date,end_date,period,suburbs)
    elif chartType == 'pointChart':
        fig = pointChart(dataset,variable,start_date,end_date,period,suburbs)
    elif chartType == 'line_bar_chart':
        fig = line_bar_chart(dataset,variable,start_date,end_date,period,suburbs)
    fig_html = fig.to_html(full_html=False)

    # Render the figure in the template
    return render_template('plot.html', fig_html=fig_html, suburbs = suburbs, variable = variable, chartType = chartType, start_date = start_date, end_date = end_date, period = period)


#Map in analysis page
# Enable CORS for all routes and origins
#CORS(app)

# Database connection details
conn = psycopg2.connect(
    dbname="climatepulse",
    user="postgres",
    password="Climatepulse123.",
    host="postgres-1.c96iysms626t.ap-southeast-2.rds.amazonaws.com",
    port=5432,
)


@app.route("/get_temperature_data", methods=["GET"])
def get_temperature_data():
    try:
        date = request.args.get("date")

        query = """
        SELECT 
            s.clusterid, 
            w.date_only,
            w.temperaturemean, 
            s.geoshape_simplified as geoshape,
            s.officialnamesuburb
        FROM suburbclustered s
        LEFT JOIN weatherdata w
        ON s.clusterid = w.clusterid
        AND w.date_only = %s;
        """

        cur = conn.cursor()
        cur.execute(query, (date,))
        rows = cur.fetchall()

        print(f"Number of suburbs fetched: {len(rows)}")

        features = []
        for row in rows:
            clusterid, datetime, temperaturemean, geoshape, officialnamesuburb = row

            # Ensure valid GeoJSON format for geometry
            if not geoshape:
                print(f"Invalid or missing geoshape for suburb: {officialnamesuburb}")
                continue

            features.append(
                {
                    "type": "Feature",
                    "geometry": geoshape,
                    "properties": {
                        "temperaturemean": temperaturemean,
                        "officialnamesuburb": officialnamesuburb,
                    },
                }
            )

        return jsonify({"type": "FeatureCollection", "features": features})

    except Exception as e:
        # Print the error for debugging
        print(f"Error: {e}")
        # Rollback the transaction in case of an error
        conn.rollback()

        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route("/get_rainfall_data", methods=["GET"])
def get_rain_data():
    try:
        date = request.args.get("date")

        query = """
        SELECT 
            s.clusterid, 
            w.date_only,
            w.rainsum, 
            s.geoshape_simplified as geoshape,
            s.officialnamesuburb
        FROM suburbclustered s
        LEFT JOIN weatherdata w
        ON s.clusterid = w.clusterid
        AND w.date_only = %s;
        """

        cur = conn.cursor()
        cur.execute(query, (date,))
        rows = cur.fetchall()

        print(f"Number of suburbs fetched: {len(rows)}")

        features = []
        for row in rows:
            clusterid, datetime, rainsum, geoshape, officialnamesuburb = row

            # Ensure valid GeoJSON format for geometry
            if not geoshape:
                print(f"Invalid or missing geoshape for suburb: {officialnamesuburb}")
                continue

            features.append(
                {
                    "type": "Feature",
                    "geometry": geoshape,
                    "properties": {
                        "rainsum": rainsum,
                        "officialnamesuburb": officialnamesuburb,
                    },
                }
            )

        return jsonify({"type": "FeatureCollection", "features": features})

    except Exception as e:
        # Print the error for debugging
        print(f"Error: {e}")
        # Rollback the transaction in case of an error
        conn.rollback()

        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route("/get_suburb_coordinates", methods=["POST"])
def get_suburb_coordinates():
    try:
        # Get the list of suburbs from the request
        suburbs = [suburb.lower() for suburb in request.json.get("suburbs", [])]

        print(suburbs)

        if not suburbs:
            return jsonify({"error": "No suburbs provided"}), 400

        # Query the database for the longitude and latitude of the suburbs
        query = """
        SELECT officialnamesuburb, lattitude, longtitude
        FROM suburbclustered
        WHERE LOWER(officialnamesuburb) = ANY(%s);;
        """
        cur = conn.cursor()
        cur.execute(query, (suburbs,))
        rows = cur.fetchall()

        # Convert the result into a list of coordinates
        coordinates = [
            {"suburb": row[0], "latitude": row[1], "longitude": row[2]} for row in rows
        ]

        return jsonify({"coordinates": coordinates})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500


@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get(
        "q", ""
    ).lower()  # Get the query parameter from the request
    if not query:
        return jsonify([])

    cur = conn.cursor()

    # Fetch matching suburbs from database (limit results to 10)
    cur.execute(
        "SELECT officialnamesuburb FROM suburbclustered WHERE LOWER(officialnamesuburb) LIKE %s LIMIT 10",
        (f"{query}%",),
    )
    results = cur.fetchall()

    # Return a list of matching suburbs
    suburbs = [row[0] for row in results]
    return jsonify(suburbs)

if __name__ == '__main__':
    app.run(debug=True)
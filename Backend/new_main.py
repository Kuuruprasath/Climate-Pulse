from retry_requests import retry
import requests_cache
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import plotly.express as px
from Conversions import convertt
import psycopg2
from flask_cors import CORS

app = Flask(__name__, template_folder=os.path.abspath('../Webpages'), static_folder=os.path.abspath('../Webpages/static'))

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


#Analysis page
# Enable CORS for all routes and origins
CORS(app)

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
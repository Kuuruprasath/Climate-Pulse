import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

def suburb_to_lat_long(suburblist):
    suburblist = tuple(suburblist)
    conn = psycopg2.connect(
        dbname="climatepulse",
        host="postgres-1.c96iysms626t.ap-southeast-2.rds.amazonaws.com",
        port=5432,
        user="postgres",
        password="Climatepulse123."
    )
    cursor = conn.cursor()
    query = "SELECT lattitude,longtitude FROM suburbclustered WHERE officialnamesuburb IN %s"
    cursor.execute(query, (suburblist,))
    dataset = cursor.fetchall()
    # first_column = [row[0] for row in dataset]
    # print(dataset)

    cursor.close()
    conn.close()
    return dataset

# print(suburb_to_lat_long(["Alpine","Clayton"]))

def suburb_to_ClusterID(suburblist):  

    # suburbs = pd.read_csv("../Actual_datasets/SuburbClustered.csv")
    # suburbs
    # filter = suburbs[suburbs["officialnamesuburb"].isin(suburblist)]
    # clusterID = filter["clusterid"]
    # return clusterID

    import psycopg2
    suburblist = tuple(suburblist)
    conn = psycopg2.connect(
        dbname="climatepulse",
        host="postgres-1.c96iysms626t.ap-southeast-2.rds.amazonaws.com",
        port=5432,
        user="postgres",
        password="Climatepulse123."
    )
    cursor = conn.cursor()
    query = "SELECT clusterid FROM suburbclustered WHERE officialnamesuburb IN %s"
    cursor.execute(query, (suburblist,))
    dataset = cursor.fetchall()
    # first_column = [row[0] for row in dataset]
    # print(dataset)

    cursor.close()
    conn.close()
    return dataset
# print(suburb_to_ClusterID(["Alpine","Clayton"]))

def clusterID_to_variables(clusterList):  
    # import pandas as pd

    # weather = pd.read_csv("../Actual_datasets/WeatherData.csv")
    # filter = weather[weather["clusterid"].isin(clusterList) ]
    # # mintemp = filter["TemperatureMin"]
    # # maxtemp = filter["TemperatureMax"]
    # # avgtemp = filter["TemperatureMean"]
    # # rain = filter["RainSum"]
    # filterdf = pd.DataFrame(filter)
    # return filterdf

    clusterlist = tuple(clusterList)
    conn = psycopg2.connect(
        dbname="climatepulse",
        host="postgres-1.c96iysms626t.ap-southeast-2.rds.amazonaws.com",
        port=5432,
        user="postgres",
        password="Climatepulse123."
    )
    cursor = conn.cursor()
    query = "SELECT clusterid, datetime, temperaturemean,rainsum FROM weatherdata WHERE clusterid IN %s"
    cursor.execute(query, (clusterlist,))
    dataset = cursor.fetchall()
    clusterid = [row[0] for row in dataset]
    datetime =  [row[1] for row in dataset]
    temperature =  [row[2] for row in dataset]
    rainfall =  [row[3] for row in dataset]

    cursor.close()
    conn.close()
    return clusterid,datetime,temperature,rainfall

# print(clusterID_to_variables([10849,106402]))
def suburb_to_var(suburblist):

    ClusterID = suburb_to_ClusterID(suburblist)
    clusterid, datetime, temperature,rainfall = clusterID_to_variables(ClusterID)
    return clusterid,datetime, temperature, rainfall
# print(suburb_to_var(["Alpine","Clayton"]))

def coordinate_to_id(latitude, longitude):
    """
    Function to get clusterid given coordinates. Find the the cluster that is closest to the input coordinates

    Input:
        latitude:
        longitude:

    Output:
        clusterid
    """

    # Connect to the database
    conn = psycopg2.connect(
    dbname="climatepulse",
    host="postgres-1.c96iysms626t.ap-southeast-2.rds.amazonaws.com",
    port=5432,
    user="postgres",
    password="Climatepulse123."
    )

    # SQL query to find the closest cluster_id using the Haversine formula
    query = """
    SELECT clusterid, lattitude, longtitude,
           ST_Distance(
               ST_SetSRID(ST_Point(longtitude, lattitude), 4326),  -- Cluster coordinates
               ST_SetSRID(ST_Point(%s, %s), 4326)               -- Input coordinates
           ) AS distance
    FROM suburbclustered
    ORDER BY distance
    LIMIT 1;
    """
    
    try:
        # Execute the query with the provided latitude and longitude
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (longitude, latitude))  # Longitude comes first in ST_Point
            result = cursor.fetchone()
            
            # Check if a result was found
            if result:
                cluster_id = result['clusterid']
                return cluster_id
            else:
                return None  # No cluster found

    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    
    finally:
        conn.close()
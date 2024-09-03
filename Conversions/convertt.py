
def suburb_to_lat_long(suburblist):
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
    import pandas as pd

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

    import psycopg2
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
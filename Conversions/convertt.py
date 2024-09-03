
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

    suburbs = pd.read_csv("../Actual_datasets/SuburbClustered.csv")
    suburbs
    filter = suburbs[suburbs["officialnamesuburb"].isin(suburblist)]
    clusterID = filter["clusterid"]
    return clusterID
# print(suburb_to_ClusterID(["Alpine","Clayton"]))

def clusterID_to_variables(clusterList):  
    import pandas as pd

    weather = pd.read_csv("../Actual_datasets/WeatherData.csv")
    filter = weather[weather["clusterid"].isin(clusterList) ]
    # mintemp = filter["TemperatureMin"]
    # maxtemp = filter["TemperatureMax"]
    # avgtemp = filter["TemperatureMean"]
    # rain = filter["RainSum"]
    filterdf = pd.DataFrame(filter)
    return filterdf
# print(clusterID_to_variables([10849,106402]))
def suburb_to_var(suburblist):
    import pandas as pd

    ClusterID = suburb_to_ClusterID(suburblist)
    variables = clusterID_to_variables(ClusterID)
    return variables
# print(suburb_to_var(["Alpine","Clayton"]))
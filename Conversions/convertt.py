
def suburb_to_lat_long(suburblist):
    import pandas as pd


    suburbs = pd.read_csv("../Actual_datasets/SuburbClustered.csv")
    filter = suburbs[suburbs["OfficialNameSuburb"].isin(suburblist)]
    latitude = filter["Latitude"]
    longtitude = filter["Longitude"]
    return [latitude,longtitude]
# print(suburb_to_lat_long(["Alpine","Clayton"]))

def suburb_to_ClusterID(suburblist):  
    import pandas as pd

    suburbs = pd.read_csv("../Actual_datasets/SuburbClustered.csv")
    suburbs
    filter = suburbs[suburbs["OfficialNameSuburb"].isin(suburblist)]
    clusterID = filter["ClusterID"]
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
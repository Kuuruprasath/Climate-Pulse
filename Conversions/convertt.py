
def suburb_to_lat_long(suburb_name):
    import pandas as pd

    suburbs = pd.read_csv("../Actual_datasets/SuburbClustered.csv")
    suburbs
    filter = suburbs[suburbs["OfficialNameSuburb"] == suburb_name]
    latitude = filter["Latitude"]
    longtitude = filter["Longitude"]
    return [latitude,longtitude]

def suburb_to_ClusterID(suburb_name):  
    import pandas as pd

    suburbs = pd.read_csv("../Actual_datasets/SuburbClustered.csv")
    suburbs
    filter = suburbs[suburbs["OfficialNameSuburb"] == suburb_name]
    clusterID = filter["ClusterID"]
    return clusterID

def clusterID_to_variables(clusterID):
    import pandas as pd
  
    weather = pd.read_csv("../Actual_datasets/WeatherData.csv")
    filter = weather[weather["ClusterID"] == clusterID]
    # mintemp = filter["TemperatureMin"]
    # maxtemp = filter["TemperatureMax"]
    # avgtemp = filter["TemperatureMean"]
    # rain = filter["RainSum"]
    filterdf = pd.DataFrame(filter)
    return filterdf
def suburb_to_var(suburb_name):
    ClusterID = suburb_to_ClusterID(suburb_name)
    variables = clusterID_to_variables(ClusterID.values[0])
    return variables
# print(suburb_to_var("Alpine"))
import pandas as pd
import pandas.io.sql as sqlio
import psycopg2
from datetime import datetime
import sys
sys.path.append('../Backend/Conversions')
import convertt

def predict_temp(suburb, years=1):
    """
    Predict temperature for one location (clusterid)

    Input: 
        suburb: suburb name
        years: number of years for future prediction
    
    Output:
        df: pandas dataframe containing clusterid, datetime, temperature, temperature_low, temperature_upper
            yhat: predicted temperature value
            yhat_lower: lower bound of the predicted temperature value
            yhat_uppwer: upper bound of the predicted temperature value
    """
    suburb = [suburb]
    id = convertt.suburb_to_ClusterID(suburb)[0]
    today = datetime.today()
    final_year =  today.replace(year = today.year + years).strftime('%Y-%m-%d')
    conn = psycopg2.connect(
        dbname="climatepulse",
        host="postgres-1.c96iysms626t.ap-southeast-2.rds.amazonaws.com",
        port=5432,
        user="postgres",
        password="Climatepulse123."
    )
    # cursor = conn.cursor()
    query = f"SELECT clusterid, datetime, temperature, temperature_low, temperature_upper FROM prediction \
        WHERE clusterid='{id}' AND datetime <= '{final_year}'"
    df = sqlio.read_sql_query(query, conn)
    # cursor.close()
    conn.close()
    
    return df

def predict_temps(suburblist, years=1):
    """
    Predict temperature for multiple locations (cluster ids)
    
    Input: 
        suburblist: list of suburbs
        years: number of years for future prediction
    
    Output:
        df: pandas dataframe containing clusterid, datetime, temperature, temperature_low, temperature_upper, suburb
            clusterid:
            datetime:
            yhat: predicted temperature value
            yhat_lower: lower bound of the predicted temperature value
            yhat_uppwer: upper bound of the predicted temperature value
            suburb:
    """

    suburblist_valid = []
    ids = []
    for i in range(len(suburblist)):
        id = convertt.suburb_to_ClusterID([suburblist[i]])
        if id:
            ids.append(id[0])
            suburblist_valid.append(suburblist[i])
    
    print(suburblist_valid)
    print(ids)
    suburb_cluster = pd.DataFrame({'suburb':suburblist_valid, 'clusterid':ids})

    # Convert ids to tuple in form of string for query
    if len(ids) == 1:
        ids = '(' + str(ids[0]) + ')'
    else:
        ids = str(tuple(ids))
        
    today = datetime.today()
    final_year =  today.replace(year = today.year + years).strftime('%Y-%m-%d')
    conn = psycopg2.connect(
        dbname="climatepulse",
        host="postgres-1.c96iysms626t.ap-southeast-2.rds.amazonaws.com",
        port=5432,
        user="postgres",
        password="Climatepulse123."
    )
    # cursor = conn.cursor()
    query = f"SELECT clusterid, datetime, temperature, temperature_low, temperature_upper FROM prediction \
        WHERE clusterid IN {ids} AND datetime <= '{final_year}'"
    df = sqlio.read_sql_query(query, conn)
    print(df)
    df = df.merge(suburb_cluster, how='left', on='clusterid')

    # cursor.close()
    conn.close()
    
    return df
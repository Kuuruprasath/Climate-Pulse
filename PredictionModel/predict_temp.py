import pandas as pd
import pandas.io.sql as sqlio
import psycopg2
from datetime import datetime
import sys
sys.path.append('../Backend/Conversions')
import convertt

def predict_temp(id, years=1):
    """
    Predict temperature for one location (clusterid)

    Input: 
        id: clusterid
        years: number of years for future prediction
    
    Output:
        df: pandas dataframe containing clusterid, datetime, yhat, yhat_lower, yhat_upper
            yhat: predicted temperature value
            yhat_lower: lower bound of the predicted temperature value
            yhat_uppwer: upper bound of the predicted temperature value
    """
    
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
    query = f"SELECT clusterid, datetime, yhat, yhat_lower, yhat_upper FROM prediction \
        WHERE clusterid='{id}' AND datetime <= '{final_year}'"
    df = sqlio.read_sql_query(query, conn)
    # cursor.close()
    conn.close()
    
    return df

def predict_temps(ids, years=1):
    """
    Predict temperature for multiple locations (cluster ids)
    
    Input: 
        ids: list of clusterid
        years: number of years for future prediction
    
    Output:
        df: pandas dataframe containing clusterid, datetime, yhat, yhat_lower, yhat_upper
            yhat: predicted temperature value
            yhat_lower: lower bound of the predicted temperature value
            yhat_uppwer: upper bound of the predicted temperature value
    """
    ids = tuple(ids) # Convert into tuple for query execution of IN
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
    query = f"SELECT clusterid, datetime, yhat, yhat_lower, yhat_upper FROM prediction \
        WHERE clusterid IN {str(ids)} AND datetime <= '{final_year}'"
    df = sqlio.read_sql_query(query, conn)
    # cursor.close()
    conn.close()
    
    return df

def suburbs_to_temp_pred(suburblist, years=1):
    """
    Predict temperature for multiple locations (list of suburbs)

    Input: 
        suburblist: list of suburbs (name)
        years: number of years for future prediction
    """
    ids = convertt.suburb_to_ClusterID(suburblist)
    suburb_cluster = pd.DataFrame({'suburb':suburblist, 'clusterid':ids})
    df = predict_temps(ids, years)
    df = df.merge(suburb_cluster, how='left', on='clusterid')

    return df
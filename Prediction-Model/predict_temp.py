import pandas.io.sql as sqlio
import psycopg2
import datetime

def predict_temp(id, years=1):
    """
    Input: 
        id: clusterid
        years: number of years for future prediction
    
    Output:
        dataset: pandas dataframe containing clusterid, datetime, yhat, yhat_lower, yhat_upper
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
    dataset = sqlio.read_sql_query(query, conn)
    # cursor.close()
    conn.close()
    
    return dataset
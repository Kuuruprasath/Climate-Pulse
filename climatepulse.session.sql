CREATE TABLE WEATHERDATA (
    ClusterID INTEGER NOT NULL,
    Datetime DATE,
    TemperatureMean FLOAT(4),
    TemperatureMax FLOAT(4),
    TemperatureMin FLOAT(4),
    RainSum FLOAT(4),
    RelativeHumidityMean FLOAT(4),
    RelativeHumidityMax FLOAT(4),
    RelativeHumidityMin FLOAT(4)
);

SELECT * FROM weatherdata;



COPY WEATHERDATA FROM '../Actual_datasets/WeatherData.csv' DELIMITER ',' CSV HEADER;




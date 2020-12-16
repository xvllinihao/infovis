'''

This file is pre-processing for app.py
In order to use app.py, first execute the main function to
generate the arrival_binning_trans.csv, departure_binning_trans.csv
save to the data/ folder

'''


import pandas as pd
import plotly.express as px
from scipy.stats import percentileofscore

airlines = pd.read_csv("../data/airlines.csv")
airports = pd.read_csv("../data/airports.csv")
delay_flights = pd.read_json("../data/delay_flights.json")
arrival_delays = pd.read_json("../data/arrival_delay_per_day.json")
departure_delays = pd.read_json("../data/departure_delay_per_day.json")
origin = pd.read_json("../data/origin.json")
destination = pd.read_json("../data/destination.json")
flights_per_day = pd.read_json("../data/flights_per_day.json")


# bin the delay time into small delay and large delay
def delay_binning(df, flag_string):
    df[flag_string+'_DELAY_WITHOUT_OUTLIER'] = df[flag_string+'_DELAY'].map(lambda x: [a for a in x if a <= 45]) # small delay less than 45 miniutes
    df[flag_string+'_DELAY_OUTLIER'] = df[flag_string+'_DELAY'].map(lambda x: [a for a in x if (180 >= a > 45)])  # large delay
    df[flag_string + '_TRANS_OUTLIER'] = df[flag_string+'_DELAY'].map\
        (lambda x: [percentileofscore(x, a, 'rank') for a in x if 180 >= a > 45]) # percentile for each large delay point
    df[flag_string + '_DELAY_MIN'] = df[flag_string + '_TRANS_OUTLIER'].map(lambda x: min(x,  default=0)) # min and max used for plot
    df[flag_string + '_DELAY_MAX'] = df[flag_string + '_TRANS_OUTLIER'].map(lambda x: max(x, default=0))
    return df


px.set_mapbox_access_token(open("../data/.mapbox_token").read())
token = open("../data/.mapbox_token").read()

city_dic = {}
airport_name_dic = {}
for idx, row in airports.iterrows():
    city_dic[row["IATA_CODE"]] = row["CITY"]
    airport_name_dic[row["IATA_CODE"]] = row["AIRPORT"]

origin_city_list = []
origin_name_list = []
for idx,row in origin.iterrows():
    origin_city_list.append(city_dic[row["ORIGIN_AIRPORT"]])
    origin_name_list.append(airport_name_dic[row["ORIGIN_AIRPORT"]])
origin["CITY"] =origin_city_list
origin["NAME"] = origin_name_list

destination_city_list = []
destination_name_list = []

for idx,row in destination.iterrows():
    destination_city_list.append(city_dic[row["DESTINATION_AIRPORT"]])
    destination_name_list.append(airport_name_dic[row["DESTINATION_AIRPORT"]])
destination["CITY"] = destination_city_list
destination["NAME"] = destination_name_list
airlines = airlines[~(airlines["IATA_CODE"] == "US")].reset_index().drop("index", axis=1) # drop 'US' airline

if __name__ == '__main__':
    # generate arrival and departure bin dataset, save to csv files
    arrival_binning = delay_binning(arrival_delays, 'ARRIVAL')
    depar_binning = delay_binning(departure_delays, 'DEPARTURE')
    arrival_binning.to_csv('data/arrival_binning_trans.csv')
    depar_binning.to_csv('data/departure_binning_trans.csv')







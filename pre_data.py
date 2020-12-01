import json
from collections import Counter, defaultdict

import pandas as pd
import numpy as np

airlines = pd.read_csv("data/airlines.csv")
airports = pd.read_csv("data/airports.csv")
flights = pd.read_csv("data/flights.csv",low_memory=False)

flights_christmas = flights[(flights["DEPARTURE_DELAY"].notnull() | flights["ARRIVAL_DELAY"].notnull()) & (flights["MONTH"]==12) & (flights["DAY"]>=18)]

tmp = flights_christmas[["AIRLINE", "ORIGIN_AIRPORT", "DESTINATION_AIRPORT","DEPARTURE_DELAY","ARRIVAL_DELAY"]].groupby(
    ["AIRLINE", "ORIGIN_AIRPORT", "DESTINATION_AIRPORT"]) \
    .size() \
    .reset_index() \
    .rename(columns={0: 'SIZE'})


delay = flights_christmas[(flights_christmas["DEPARTURE_DELAY"]>0) | (flights_christmas["ARRIVAL_DELAY"]>0)].groupby(
    ["AIRLINE", "ORIGIN_AIRPORT", "DESTINATION_AIRPORT"]) \
    .size() \
    .reset_index() \
    .rename(columns={0: 'DELAY'})

tmp = pd.merge(tmp,delay, on=["AIRLINE", "ORIGIN_AIRPORT", "DESTINATION_AIRPORT"])

delay_rate = []
for size,delay in zip(tmp["SIZE"],tmp["DELAY"]):
    delay_rate.append(delay/size)

tmp["DELAY_RATE"] = delay_rate
tmp = tmp[tmp["DELAY"].notna() & tmp["DELAY_RATE"].notna()]
print(tmp)
#
location_map = {}
for airport, lon, lat in zip(airports["IATA_CODE"],airports["LONGITUDE"],airports["LATITUDE"]):
    location_map[airport] = {"lon":lon, "lat":lat}

dict = {}

for airline in airlines["IATA_CODE"]:
    dict[airline] = tmp[tmp["AIRLINE"]==airline]
    start_lat = []
    start_lon = []
    end_lat = []
    end_lon = []

    for start_airport in dict[airline]["ORIGIN_AIRPORT"]:
        start_lat.append(location_map[start_airport]["lat"])
        start_lon.append(location_map[start_airport]["lon"])

    for end_airport in dict[airline]["DESTINATION_AIRPORT"]:
        end_lat.append(location_map[end_airport]["lat"])
        end_lon.append(location_map[end_airport]["lon"])

    dict[airline]["ORIGIN_LAT"] = start_lat
    dict[airline]["ORIGIN_LON"] = start_lon
    dict[airline]["DESTINATION_LAT"] = end_lat
    dict[airline]["DESTINATION_LON"] = end_lon


res = pd.DataFrame()

for data in dict.keys():
   res = res.append(dict[data])
print(res)

res.to_json("data/delay_flights.json")


flights_sum = flights_christmas[["AIRLINE","MONTH","DAY","ARRIVAL_DELAY"]]
flights_sum = flights_sum[flights_sum["ARRIVAL_DELAY"]>0]
arrival_delay_per_day = flights_sum.groupby(["AIRLINE","MONTH","DAY"])["ARRIVAL_DELAY"].apply(list).reset_index()
df = pd.DataFrame({
    'year': [2015]*len(arrival_delay_per_day["MONTH"]),
    'month':arrival_delay_per_day["MONTH"],
    "day": arrival_delay_per_day["DAY"]
})

df = pd.to_datetime(df)
arrival_delay_per_day["DATE"] = df
arrival_delay_per_day = arrival_delay_per_day[["AIRLINE","DATE","ARRIVAL_DELAY"]]
print(arrival_delay_per_day)
arrival_delay_per_day.to_json("data/arrival_delay_per_day.json")

flights_sum = flights_christmas[["AIRLINE","MONTH","DAY","DEPARTURE_DELAY"]]
flights_sum = flights_sum[flights_sum["DEPARTURE_DELAY"]>0]
departure_delay_per_day = flights_sum.groupby(["AIRLINE","MONTH","DAY"])["DEPARTURE_DELAY"].apply(list).reset_index()
df = pd.DataFrame({
    'year': [2015]*len(departure_delay_per_day["MONTH"]),
    'month':departure_delay_per_day["MONTH"],
    "day": departure_delay_per_day["DAY"]
})

df = pd.to_datetime(df)
departure_delay_per_day["DATE"] = df
departure_delay_per_day_delay_per_day = departure_delay_per_day[["AIRLINE","DATE","DEPARTURE_DELAY"]]
print(departure_delay_per_day)
departure_delay_per_day.to_json("data/departure_delay_per_day.json")




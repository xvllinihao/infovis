import ast

import pandas as pd


airports = pd.read_csv("data/airports.csv")
flights = pd.read_csv("data/flights.csv",low_memory=False)

flights_christmas = flights[(flights["MONTH"]==12) & (flights["DAY"]>=18)]




#画机场图的数据
origin_flights_sum = flights_christmas.groupby(["ORIGIN_AIRPORT","DESTINATION_AIRPORT","DAY","MONTH"]).size().reset_index().rename(columns={0:"SIZE"})
origin_flights_sum_dict = {}

for idx,row in origin_flights_sum.iterrows():
    origin_flights_sum_dict[row["ORIGIN_AIRPORT"]+row["DESTINATION_AIRPORT"]+str(row["DAY"])+str(row["MONTH"])] = row["SIZE"]
print(origin_flights_sum_dict)


origin_destinations = flights_christmas.groupby(["ORIGIN_AIRPORT","DAY","MONTH"])["DESTINATION_AIRPORT"].apply(set).reset_index()
flights_sum_list = []
for idx,row in origin_destinations.iterrows():
    tmp_list=[]
    for des in row["DESTINATION_AIRPORT"]:
        tmp_list.append(origin_flights_sum_dict[row["ORIGIN_AIRPORT"]+des+str(row["DAY"])+str(row["MONTH"])])
    flights_sum_list.append(tmp_list)
origin_destinations["FLIGHT_SUM"] = flights_sum_list
df = pd.DataFrame({
    'year': [2015]*len(origin_destinations["MONTH"]),
    'month':origin_destinations["MONTH"],
    "day": origin_destinations["DAY"]
})

df = pd.to_datetime(df)
origin_destinations["DATE"] = df
origin_destinations = origin_destinations[["ORIGIN_AIRPORT","DATE","DESTINATION_AIRPORT","FLIGHT_SUM"]]

origin_destinations.to_json("data/processed_airports.json")
print(origin_destinations)


#画雷达图的数据
tmp = flights_christmas[["DAY","MONTH","DEPARTURE_DELAY","DEPARTURE_TIME"]]
tmp = tmp[tmp["DEPARTURE_DELAY"].notna() & tmp["DEPARTURE_TIME"].notna()]
tmp1 = tmp[tmp["DEPARTURE_DELAY"]>0]
departure_time = []


for idx,row in tmp.iterrows():
    time = int(row["DEPARTURE_TIME"]//100) %24
    departure_time.append(time)

tmp["DEPARTURE_TIME"] = departure_time
departure_time = []
for idx,row in tmp1.iterrows():
    time = int(row["DEPARTURE_TIME"]//100) % 24
    departure_time.append(time)

tmp1["DEPARTURE_TIME"] = departure_time
on_time_rate = []




tmp = tmp.groupby(["DAY","MONTH","DEPARTURE_TIME"]).size().reset_index().rename(columns={0:"TOTAL"})
tmp1 = tmp1.groupby(["DAY","MONTH","DEPARTURE_TIME"]).size().reset_index().rename(columns={0:"DELAY"})
for total, deley in zip(tmp["TOTAL"],tmp1["DELAY"]):
    on_time_rate.append(1-deley/total)
tmp["ON_TIME_RATE"] = on_time_rate
df = pd.DataFrame({
    'year': [2015]*len(tmp["MONTH"]),
    'month':tmp["MONTH"],
    "day": tmp["DAY"]
})

df = pd.to_datetime(df)
tmp["DATE"] = df
tmp = tmp[["DATE","DEPARTURE_TIME","ON_TIME_RATE"]]
tmp.to_json("data/on_time_list.json")
print(tmp)
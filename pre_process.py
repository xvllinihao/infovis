import ast

import pandas as pd


airports = pd.read_csv("data/airports.csv")
flights = pd.read_csv("data/flights.csv",low_memory=False)

flights_christmas = flights[(flights["MONTH"]==12) & (flights["DAY"]>=18)]




#画机场图的数据
origin_flights_sum = flights_christmas.groupby(["ORIGIN_AIRPORT","DESTINATION_AIRPORT","DAY","MONTH"]).size().reset_index().rename(columns={0:"SIZE"})
origin_flights_sum_dict = {}
flights_delay_dict = {}




for idx,row in origin_flights_sum.iterrows():
    origin_flights_sum_dict[row["ORIGIN_AIRPORT"]+row["DESTINATION_AIRPORT"]+str(row["DAY"])+str(row["MONTH"])] = row["SIZE"]
    delay_times = flights_christmas[(flights_christmas["ORIGIN_AIRPORT"]==row["ORIGIN_AIRPORT"]) & (flights_christmas["DESTINATION_AIRPORT"]==row["DESTINATION_AIRPORT"]) & (flights_christmas["DAY"]==row["DAY"])]
    delay_times = delay_times[delay_times["DEPARTURE_DELAY"]>0]
    delay_times = delay_times[["ORIGIN_AIRPORT","DESTINATION_AIRPORT","DAY","MONTH","DEPARTURE_DELAY","DEPARTURE_TIME"]]
    less_than_30 = []
    less_than_60 = []
    more_than_60 = []
    for index,Row in delay_times.iterrows():
        if Row["DEPARTURE_DELAY"] <= 30:
            less_than_30.append((Row["DEPARTURE_DELAY"],Row["DEPARTURE_TIME"]))
        elif 30<Row["DEPARTURE_DELAY"]<=60:
            less_than_60.append((Row["DEPARTURE_DELAY"],Row["DEPARTURE_TIME"]))
        else:
            more_than_60.append((Row["DEPARTURE_DELAY"], Row["DEPARTURE_TIME"]))
    flights_delay_dict[Row["ORIGIN_AIRPORT"]+Row["DESTINATION_AIRPORT"]+str(Row["DAY"])+str(Row["MONTH"])+"first_seg"] =  less_than_30
    flights_delay_dict[Row["ORIGIN_AIRPORT"] + Row["DESTINATION_AIRPORT"] + str(Row["DAY"]) + str(
        Row["MONTH"]) + "second_seg"] = less_than_60
    flights_delay_dict[Row["ORIGIN_AIRPORT"] + Row["DESTINATION_AIRPORT"] + str(Row["DAY"]) + str(
        Row["MONTH"]) + "third_seg"] = more_than_60



origin_destinations = flights_christmas.groupby(["ORIGIN_AIRPORT","DAY","MONTH"])["DESTINATION_AIRPORT"].apply(set).reset_index()

flights_sum_list = []
first_segment = []
second_segment = []
third_segment = []
for idx,row in origin_destinations.iterrows():
    tmp_list=[]
    tmp_first_segment = []
    tmp_second_segment = []
    tmp_third_segment = []
    for des in row["DESTINATION_AIRPORT"]:
        tmp_list.append(origin_flights_sum_dict[row["ORIGIN_AIRPORT"]+des+str(row["DAY"])+str(row["MONTH"])])
        first_segment.append(flights_delay_dict[row["ORIGIN_AIRPORT"]+des+str(row["DAY"])+str(row["MONTH"])+"first_seg"])
        tmp_second_segment.append(
            flights_delay_dict[row["ORIGIN_AIRPORT"] + des + str(row["DAY"]) + str(row["MONTH"]) + "second_seg"])
        tmp_third_segment.append(
            flights_delay_dict[row["ORIGIN_AIRPORT"] + des + str(row["DAY"]) + str(row["MONTH"]) + "third_seg"])
    flights_sum_list.append(tmp_list)
    first_segment.append(tmp_first_segment)
    second_segment.append(tmp_second_segment)
    third_segment.append(tmp_third_segment)

origin_destinations["FLIGHT_SUM"] = flights_sum_list
origin_destinations["FIRST_SEG"] = first_segment
origin_destinations["SECOND_SEG"] = second_segment
origin_destinations["THIRD_SEG"] = third_segment
df = pd.DataFrame({
    'year': [2015]*len(origin_destinations["MONTH"]),
    'month':origin_destinations["MONTH"],
    "day": origin_destinations["DAY"]
})

df = pd.to_datetime(df)
origin_destinations["DATE"] = df
origin_destinations = origin_destinations[["ORIGIN_AIRPORT","DATE","DESTINATION_AIRPORT","FLIGHT_SUM","FIRST_SEG","SECOND_SEG","THIRD_SEG"]]

origin_destinations.to_json("data/processed_airports.json")
print(origin_destinations)
#
#
# #画雷达图的数据
# tmp = flights_christmas[["DAY","MONTH","DEPARTURE_DELAY","DEPARTURE_TIME"]]
# tmp = tmp[tmp["DEPARTURE_DELAY"].notna() & tmp["DEPARTURE_TIME"].notna()]
# tmp1 = tmp[tmp["DEPARTURE_DELAY"]>0]
# departure_time = []
# time_segment = []
#
# for idx,row in tmp.iterrows():
#     time = int(row["DEPARTURE_TIME"]//100) %24
#     departure_time.append(time)
#     if 0<=time<6:
#         time_segment.append("MIDNIGHT")
#     elif 6<=time<12:
#         time_segment.append("MORNING")
#     elif 12<=time<18:
#         time_segment.append("AFTERNOON")
#     elif 18<=time<24:
#         time_segment.append("EVENING")
#
#
# tmp["DEPARTURE_TIME"] = departure_time
# tmp["TIME_SEGMENT"] = time_segment
#
# time_segment = []
# departure_time = []
# for idx,row in tmp1.iterrows():
#     time = int(row["DEPARTURE_TIME"]//100) % 24
#     departure_time.append(time)
#     if 0<=time<6:
#         time_segment.append("MIDNIGHT")
#     elif 6<=time<12:
#         time_segment.append("MORNING")
#     elif 12<=time<18:
#         time_segment.append("AFTERNOON")
#     elif 18<=time<24:
#         time_segment.append("EVENING")
#
# tmp1["DEPARTURE_TIME"] = departure_time
# tmp1["TIME_SEGMENT"] =time_segment
# on_time_rate = []
#
#
#
#
# tmp = tmp.groupby(["DAY","MONTH","DEPARTURE_TIME","TIME_SEGMENT"]).size().reset_index().rename(columns={0:"TOTAL"})
# tmp1 = tmp1.groupby(["DAY","MONTH","DEPARTURE_TIME","TIME_SEGMENT"]).size().reset_index().rename(columns={0:"DELAY"})
# for total, deley in zip(tmp["TOTAL"],tmp1["DELAY"]):
#     on_time_rate.append(1-deley/total)
# tmp["ON_TIME_RATE"] = on_time_rate
# df = pd.DataFrame({
#     'year': [2015]*len(tmp["MONTH"]),
#     'month':tmp["MONTH"],
#     "day": tmp["DAY"]
# })
# df = pd.to_datetime(df)
# tmp["DATE"] = df
# tmp = tmp[["DATE","DEPARTURE_TIME","ON_TIME_RATE","TOTAL","TIME_SEGMENT"]]
# tmp.to_json("data/on_time_list.json")
# print(tmp)

#画overview的数据
# over_view_origin_destinations = flights_christmas.groupby(["ORIGIN_AIRPORT"])["DESTINATION_AIRPORT"].apply(set).reset_index()
# print(over_view_origin_destinations)
# over_view_origin_destinations.to_json("data/overview_destinations.json")


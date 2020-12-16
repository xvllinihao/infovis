import ast

import pandas as pd


def segment_time(x):
    if 0<x<30:
        return 1
    elif 30<=x<60:
        return 2
    elif x>=60:
        return 3
    elif x<=0:
        return 0

def transform_the_time(x):
    hours = x//100
    minutes= (x%100)/60
    return hours+minutes


airports = pd.read_csv("../data/airports.csv")
flights = pd.read_csv("data/flights.csv",low_memory=False)


flights_christmas = flights[(flights["MONTH"]==12) & (flights["DAY"]>=18)]
flights_christmas["DELAY_SEG"] = flights_christmas["DEPARTURE_DELAY"].map(segment_time)
flights_christmas["DEPARTURE_TIME"] = flights_christmas["DEPARTURE_TIME"].map(transform_the_time)


tmp = flights_christmas.groupby(["ORIGIN_AIRPORT","DAY","MONTH","DESTINATION_AIRPORT","DELAY_SEG"])["DEPARTURE_TIME"].apply(list).reset_index()
tmp2 = flights_christmas.groupby(["ORIGIN_AIRPORT","DAY","MONTH","DESTINATION_AIRPORT","DELAY_SEG"])["DEPARTURE_DELAY"].apply(list).reset_index()
tmp = pd.merge(tmp,tmp2,on=["ORIGIN_AIRPORT","DAY","MONTH","DESTINATION_AIRPORT","DELAY_SEG"])
df = pd.DataFrame({
    'year': [2015]*len(tmp["MONTH"]),
    'month':tmp["MONTH"],
    "day": tmp["DAY"]
})

df = pd.to_datetime(df)
tmp["DATE"] = df

tmp.to_json("data/detail_delay_information.json")
print(tmp)


#画机场图的数据
# origin_flights_sum = flights_christmas.groupby(["ORIGIN_AIRPORT","DESTINATION_AIRPORT","DAY","MONTH"]).size().reset_index().rename(columns={0:"SIZE"})
# origin_flights_sum_dict = {}
#
#
#
#
#
# for idx,row in origin_flights_sum.iterrows():
#     origin_flights_sum_dict[row["ORIGIN_AIRPORT"]+row["DESTINATION_AIRPORT"]+str(row["DAY"])+str(row["MONTH"])] = row["SIZE"]
#
#
# origin_destinations = flights_christmas.groupby(["ORIGIN_AIRPORT","DAY","MONTH"])["DESTINATION_AIRPORT"].apply(set).reset_index()
# flights_sum_list = []
# for idx,row in origin_destinations.iterrows():
#     tmp_list=[]
#     tmp_first_segment = []
#     tmp_second_segment = []
#     tmp_third_segment = []
#     for des in row["DESTINATION_AIRPORT"]:
#         tmp_list.append(origin_flights_sum_dict[row["ORIGIN_AIRPORT"]+des+str(row["DAY"])+str(row["MONTH"])])
#
#         # flights_delay_dict[Row["ORIGIN_AIRPORT"] + Row["DESTINATION_AIRPORT"] + str(Row["DAY"]) + str(
#         #     Row["MONTH"]) + "first_seg"] = less_than_30
#         # flights_delay_dict[Row["ORIGIN_AIRPORT"] + Row["DESTINATION_AIRPORT"] + str(Row["DAY"]) + str(
#         #     Row["MONTH"]) + "second_seg"] = less_than_60
#         # flights_delay_dict[Row["ORIGIN_AIRPORT"] + Row["DESTINATION_AIRPORT"] + str(Row["DAY"]) + str(
#         #     Row["MONTH"]) + "third_seg"] = more_than_60
#
#     flights_sum_list.append(tmp_list)
#
# origin_destinations["FLIGHT_SUM"] = flights_sum_list
#
# df = pd.DataFrame({
#     'year': [2015]*len(origin_destinations["MONTH"]),
#     'month':origin_destinations["MONTH"],
#     "day": origin_destinations["DAY"]
# })
#
# df = pd.to_datetime(df)
# origin_destinations["DATE"] = df
# origin_destinations = origin_destinations[["ORIGIN_AIRPORT","DATE","DESTINATION_AIRPORT","FLIGHT_SUM"]]
#
# origin_destinations.to_json("data/processed_airports.json")
# print(origin_destinations)
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


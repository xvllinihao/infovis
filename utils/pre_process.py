"""

"""

import pandas as pd


def segment_time(x):
    if 0 < x < 30:
        return 1
    elif 30 <= x < 60:
        return 2
    elif x >= 60:
        return 3
    elif x <= 0:
        return 0


def transform_the_time(x):
    hours = x // 100
    minutes = (x % 100) / 60
    return hours + minutes


airports = pd.read_csv("../data/airports.csv")
flights = pd.read_csv("data/flights.csv", low_memory=False)

flights_christmas = flights[(flights["MONTH"] == 12) & (flights["DAY"] >= 18)]

# data used to plotting the detail delay information
flights_christmas["DELAY_SEG"] = flights_christmas["DEPARTURE_DELAY"].map(segment_time)
flights_christmas["DEPARTURE_TIME"] = flights_christmas["DEPARTURE_TIME"].map(transform_the_time)

delay_seg = flights_christmas.groupby(["ORIGIN_AIRPORT", "DAY", "MONTH", "DESTINATION_AIRPORT", "DELAY_SEG"])[
    "DEPARTURE_TIME"].apply(list).reset_index()
deparature_delay = flights_christmas.groupby(["ORIGIN_AIRPORT", "DAY", "MONTH", "DESTINATION_AIRPORT", "DELAY_SEG"])[
    "DEPARTURE_DELAY"].apply(list).reset_index()
detail_delay_information = pd.merge(delay_seg, deparature_delay, on=["ORIGIN_AIRPORT", "DAY", "MONTH", "DESTINATION_AIRPORT", "DELAY_SEG"])
df = pd.DataFrame({
    'year': [2015] * len(detail_delay_information["MONTH"]),
    'month': detail_delay_information["MONTH"],
    "day": detail_delay_information["DAY"]
})
df = pd.to_datetime(df)
detail_delay_information["DATE"] = df

detail_delay_information.to_json("data/detail_delay_information.json")
# print(tmp)


# data of drawing the airport
origin_flights_sum = flights_christmas.groupby(
    ["ORIGIN_AIRPORT", "DESTINATION_AIRPORT", "DAY", "MONTH"]).size().reset_index().rename(columns={0: "SIZE"})
origin_flights_sum_dict = {}

for idx, row in origin_flights_sum.iterrows():
    origin_flights_sum_dict[row["ORIGIN_AIRPORT"] + row["DESTINATION_AIRPORT"] + str(row["DAY"]) + str(row["MONTH"])] = \
    row["SIZE"]

origin_destinations = flights_christmas.groupby(["ORIGIN_AIRPORT", "DAY", "MONTH"])["DESTINATION_AIRPORT"].apply(
    set).reset_index()
flights_sum_list = []

for idx, row in origin_destinations.iterrows():
    tmp_list = []
    for des in row["DESTINATION_AIRPORT"]:
        tmp_list.append(origin_flights_sum_dict[row["ORIGIN_AIRPORT"] + des + str(row["DAY"]) + str(row["MONTH"])])

    flights_sum_list.append(tmp_list)

origin_destinations["FLIGHT_SUM"] = flights_sum_list

df = pd.DataFrame({
    'year': [2015] * len(origin_destinations["MONTH"]),
    'month': origin_destinations["MONTH"],
    "day": origin_destinations["DAY"]
})

df = pd.to_datetime(df)
origin_destinations["DATE"] = df
origin_destinations = origin_destinations[["ORIGIN_AIRPORT", "DATE", "DESTINATION_AIRPORT", "FLIGHT_SUM"]]

origin_destinations.to_json("data/processed_airports.json")
print(origin_destinations)

# data of plotting the sunburst
tmp = flights_christmas[["DAY", "MONTH", "DEPARTURE_DELAY", "DEPARTURE_TIME"]]
tmp = tmp[tmp["DEPARTURE_DELAY"].notna() & tmp["DEPARTURE_TIME"].notna()]
tmp1 = tmp[tmp["DEPARTURE_DELAY"] > 0]
departure_time = []
time_segment = []

for idx, row in tmp.iterrows():
    time = int(row["DEPARTURE_TIME"] // 100) % 24
    departure_time.append(time)
    if 0 <= time < 6:
        time_segment.append("MIDNIGHT")
    elif 6 <= time < 12:
        time_segment.append("MORNING")
    elif 12 <= time < 18:
        time_segment.append("AFTERNOON")
    elif 18 <= time < 24:
        time_segment.append("EVENING")

tmp["DEPARTURE_TIME"] = departure_time
tmp["TIME_SEGMENT"] = time_segment

time_segment = []
departure_time = []
for idx, row in tmp1.iterrows():
    time = int(row["DEPARTURE_TIME"] // 100) % 24
    departure_time.append(time)
    if 0 <= time < 6:
        time_segment.append("MIDNIGHT")
    elif 6 <= time < 12:
        time_segment.append("MORNING")
    elif 12 <= time < 18:
        time_segment.append("AFTERNOON")
    elif 18 <= time < 24:
        time_segment.append("EVENING")

tmp1["DEPARTURE_TIME"] = departure_time
tmp1["TIME_SEGMENT"] = time_segment
on_time_rate = []

tmp = tmp.groupby(["DAY", "MONTH", "DEPARTURE_TIME", "TIME_SEGMENT"]).size().reset_index().rename(columns={0: "TOTAL"})
tmp1 = tmp1.groupby(["DAY", "MONTH", "DEPARTURE_TIME", "TIME_SEGMENT"]).size().reset_index().rename(
    columns={0: "DELAY"})
for total, deley in zip(tmp["TOTAL"], tmp1["DELAY"]):
    on_time_rate.append(1 - deley / total)
tmp["ON_TIME_RATE"] = on_time_rate
df = pd.DataFrame({
    'year': [2015] * len(tmp["MONTH"]),
    'month': tmp["MONTH"],
    "day": tmp["DAY"]
})
df = pd.to_datetime(df)
tmp["DATE"] = df
tmp = tmp[["DATE", "DEPARTURE_TIME", "ON_TIME_RATE", "TOTAL", "TIME_SEGMENT"]]
tmp.to_json("data/on_time_list.json")
print(tmp)

# data of over_view
over_view_origin_destinations = flights_christmas.groupby(["ORIGIN_AIRPORT"])["DESTINATION_AIRPORT"].apply(
    set).reset_index()
print(over_view_origin_destinations)
over_view_origin_destinations.to_json("data/overview_destinations.json")

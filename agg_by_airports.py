import pandas as pd

airlines = pd.read_csv("data/airlines.csv")
airports = pd.read_csv("data/airports.csv")
flights = pd.read_csv("data/flights.csv",low_memory=False)

flights_christmas = flights[(flights["MONTH"]==12) & (flights["DAY"]>=18)]
flights_christmas_delay = flights[(flights["MONTH"]==12) & (flights["DAY"]>=18) & ((flights["ARRIVAL_DELAY"]>0) | (flights["DEPARTURE_DELAY"]>0))]

# location_map = {}
# for airport, lon, lat in zip(airports["IATA_CODE"],airports["LONGITUDE"],airports["LATITUDE"]):
#     location_map[airport] = {"lon":lon, "lat":lat}
#
# origins = flights_christmas.groupby(
#     ["ORIGIN_AIRPORT"]) \
#     .size() \
#     .reset_index() \
#     .rename(columns={0: 'SUM'})
#
# origin_delay = flights_christmas_delay.groupby(
#     ["ORIGIN_AIRPORT"]) \
#     .size() \
#     .reset_index() \
#     .rename(columns={0: 'DELAY_SUM'})
#
# origins = pd.merge(origins,origin_delay,on="ORIGIN_AIRPORT",how="outer")
#
# origin_delay_rate = []
# for sum,delay in zip(origins["SUM"],origins["DELAY_SUM"]):
#     if isinstance(delay,float):
#         origin_delay_rate.append(delay/sum)
#     else:
#         origin_delay_rate.append(1)
# longitude = []
# latitude = []
#
# for airport in origins["ORIGIN_AIRPORT"]:
#     longitude.append(location_map[airport]["lon"])
#     latitude.append(location_map[airport]["lat"])
#
# origins["LON"] = longitude
# origins["LAT"] = latitude
# origins["DELAY_RATE"] = origin_delay_rate
# origins.to_json("data/origin.json")
# print(origins)
#
# destinations = flights_christmas.groupby(
#     ["DESTINATION_AIRPORT"]) \
#     .size() \
#     .reset_index() \
#     .rename(columns={0: 'SUM'})
#
# destination_delay = flights_christmas_delay.groupby(
#     ["DESTINATION_AIRPORT"]) \
#     .size() \
#     .reset_index() \
#     .rename(columns={0: 'DELAY'})
#
# destinations = pd.merge(destinations,destination_delay, how="outer", on="DESTINATION_AIRPORT")
#
# destination_delay_rate = []
# for sum,delay in zip(destinations["SUM"],destinations["DELAY"]):
#     if isinstance(delay,int):
#         destination_delay_rate.append(delay/sum)
#     else:
#         destination_delay_rate.append(1)
#
# destinations["LON"] = longitude
# destinations["LAT"] = latitude
# destinations["DELAY_RATE"] = destination_delay_rate
#
# destinations.to_json("data/destination.json")
# print(destinations)

flights_per_day = flights_christmas.groupby(["MONTH", "DAY"]).size().reset_index().rename(columns={0: "SUM"})
df = pd.DataFrame({
    'year': [2015]*len(flights_per_day["MONTH"]),
    'month':flights_per_day["MONTH"],
    "day": flights_per_day["DAY"]
})

df = pd.to_datetime(df)
flights_per_day["DATE"] = df
flights_per_day = flights_per_day[["DATE","SUM"]]
flights_per_day.to_json("data/flights_per_day.json")
print(flights_per_day)

delays_per_day = flights_christmas_delay.groupby(["MONTH", "DAY"]).size().reset_index().rename(columns={0: "SUM"})
df = pd.DataFrame({
    'year': [2015]*len(delays_per_day["MONTH"]),
    'month':delays_per_day["MONTH"],
    "day": delays_per_day["DAY"]
})

df = pd.to_datetime(df)
delays_per_day["DATE"] = df
delays_per_day = delays_per_day[["DATE","SUM"]]
delays_per_day.to_json("data/delays_per_day.json")
print(delays_per_day)
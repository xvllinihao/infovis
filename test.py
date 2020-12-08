import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash import callback_context
from dash.dependencies import Output, Input, State
import plotly.express as px
from plotly.subplots import make_subplots

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


airports = pd.read_json("data/processed_airports.json")
airports_info = pd.read_csv("data/airports.csv")
on_time_list = pd.read_json("data/on_time_list.json")

location_dic = {}
for idx,row in airports_info.iterrows():
    location_dic[row["IATA_CODE"]] = {"lat":row["LATITUDE"], "lon":row["LONGITUDE"]}

app.layout = html.Div(children=[
    dbc.Card(children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                    dcc.Dropdown(
                        id='date_menu',
                        options=[{'label': pd.to_datetime(timestamp).strftime('%Y.%m.%d'), 'value': timestamp} for
                                 timestamp in airports["DATE"].unique()],
                        value=airports["DATE"].unique()[0],
                    ),
                    dcc.Graph(
                        id="map",
                    ), ]),
                dbc.Col(
                    id='info_box'
                )
            ]
        )
    ]
    )
]
)

@app.callback(
    Output('map','figure'),
    [Input('map','selectedData'),Input('date_menu','value'), Input("map","hoverData")],
)
def update_click_map(selectedData,date,hoverData):
    """
    单击地图上的点选定要看的机场，双击取消选定，有时候会有bug，后面研究一哈
    :param selectedData:
    :param date:
    :param hoverData:
    :return:
    """
    timestamp = pd.to_datetime(date)
    fig = px.scatter_geo(
        airports_info,
        scope="usa",
        lat=airports_info["LATITUDE"],
        lon=airports_info["LONGITUDE"],
        hover_name=airports_info["IATA_CODE"],)

    fig.update_layout(clickmode="event+select")
    fig.update_layout(hovermode="closest")

    if selectedData:
        point_dict = selectedData["points"][0]
        origin_lon = point_dict['lon']
        origin_lat = point_dict['lat']
        airport = point_dict['hovertext']

        infos = airports[(airports["ORIGIN_AIRPORT"]==airport) & (airports["DATE"]==timestamp)]
        destinations = infos["DESTINATION_AIRPORT"].tolist()[0] if infos["DESTINATION_AIRPORT"].tolist() else []
        points = airports_info[airports_info["IATA_CODE"].isin(destinations) | (airports_info["IATA_CODE"]==airport)]

        fig = px.scatter_geo(
            airports_info,
            scope="usa",
            lat=points["LATITUDE"],
            lon=points["LONGITUDE"],
            hover_name=points["IATA_CODE"],
            hover_data=None
        )

        fig.update_layout(clickmode="event+select")

        for des in destinations:
            fig.add_trace(
                go.Scattergeo(
                    lon=[origin_lon, location_dic[des]["lon"]],
                    lat=[origin_lat, location_dic[des]["lat"]],
                    mode="lines",
                    line = dict(width=1,color='red'),
                    marker=dict(color='red'),
                    hoverinfo="skip",
                    showlegend=False
                )
            )
        return fig

    # hover的时候显示hover的点可以去到的机场
    elif hoverData:
        point_dict = hoverData["points"][0]
        origin_lon = point_dict['lon']
        origin_lat = point_dict['lat']
        airport = point_dict['hovertext']

        infos = airports[(airports["ORIGIN_AIRPORT"]==airport) & (airports["DATE"]==timestamp)]
        destinations = infos["DESTINATION_AIRPORT"].tolist()[0] if infos["DESTINATION_AIRPORT"].tolist() else []
        for des in destinations:
            fig.add_trace(
                go.Scattergeo(
                    lon=[origin_lon, location_dic[des]["lon"]],
                    lat=[origin_lat, location_dic[des]["lat"]],
                    mode="lines",
                    line = dict(width=1,color='red'),
                    hoverinfo="skip",
                    showlegend=False
                )
            )
        return fig
    else:
        return fig

@app.callback(
    Output('info_box','children'),
    [Input('map','selectedData'),Input('date_menu','value')]
)
def update_infobox(selectedData,date):
    timestamp = pd.to_datetime(date)
    data = on_time_list[on_time_list["DATE"]==timestamp]
    #我处理的时候是int型的，会默认转成度数，要换成str才能24等分
    time_list = data["DEPARTURE_TIME"].tolist()
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i])+":00"
    data["DEPARTURE_TIME"] = time_list

    #没有选定数据的时候就显示雷达图
    if not selectedData:
        obj = dcc.Graph(
            figure = px.line_polar(
                data,
                r= "ON_TIME_RATE",
                theta="DEPARTURE_TIME",
                line_close=True
            )
        )
        return obj


    #有选定数据就显示卡片
    else:
        point_dict = selectedData["points"][0]
        airport = point_dict['hovertext']
        infos = airports_info[airports_info["IATA_CODE"]==airport]
        detailed_infos = airports[(airports["ORIGIN_AIRPORT"] == airport) & (airports["DATE"] == timestamp)]
        destinations = detailed_infos["DESTINATION_AIRPORT"].tolist()[0] if detailed_infos["DESTINATION_AIRPORT"].tolist() else []
        destinations_num = detailed_infos["FLIGHT_SUM"].tolist()[0] if detailed_infos["FLIGHT_SUM"].tolist() else []
        df = pd.DataFrame()
        df["destination"] = destinations
        df["nums"] = destinations_num
        df = df.nlargest(5,"nums")
        table_header = [
            html.Thead(html.Tr([html.Th("Destination"),html.Th("Flights_sum")]))
        ]
        table_body = [html.Tbody([html.Tr([html.Td(row["destination"]),html.Td(row["nums"])]) for idx, row in df.iterrows()])]
        total_flights = sum(destinations_num)

        obj = dbc.Card(children=[
            html.H4("IATA_CODE: {}".format(airport)),
            html.H6("AIRPORT_NAME: {}".format(infos["AIRPORT"].values[0])),
            html.H6("CITY_NAMR: {}".format(infos["CITY"].values[0])),
            html.H6("TOTAL_FILGHTS: {}".format(total_flights)),
            html.H6("Hottest Destinations"),
            dbc.Table(table_header+table_body,bordered=True)
            ]
        )
        return obj

if __name__ == '__main__':
    app.run_server(debug=True)

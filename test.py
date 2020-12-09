import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
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
numFlight = pd.read_csv("data/num_flights_per_day.csv")
delay = pd.read_csv("data/delay_per_day.csv")

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
        ),
        dbc.Row(children=[
            dbc.Col(children=[
                dcc.Checklist(id="DOF", options=[{"label":"# flights", "value":"flights"},{"label":"% Delay", "value":"delay"}],
                               value=["flights"])
            ],width={"size": 6, "offset": 2})
            ,
        ]),
        dbc.Row(children=[
            dcc.Graph(id="line"),
        ])
    ]
    )
]
)

@app.callback(
    Output('line','figure'),
    [Input('DOF','value'), Input("map","selectedData")],
)
def update_line_chart(selectedDOF, selectedData):
    fig = px.line(numFlight, x="date", y="count", color="ORIGIN_AIRPORT")
    if selectedData:
        airport = selectedData["points"][0]['hovertext']
        print(airport)
        print((selectedDOF))
        if selectedDOF == ["flights"]:
            info = numFlight[(numFlight["ORIGIN_AIRPORT"]==airport)]
            fig = px.line(info, x="date", y="count")
            return fig
        elif selectedDOF == ["delay"]:
            info = delay[(delay["ORIGIN_AIRPORT"]==airport)]
            fig = px.line(info, x="date", y="delay")
            return fig
        elif (selectedDOF == ["flights","delay"] or selectedDOF == ["delay","flights"]):
            info1 = delay[(delay["ORIGIN_AIRPORT"] == airport)]
            info2 = numFlight[(numFlight["ORIGIN_AIRPORT"] == airport)]
            trace1 = go.Scatter(
                x=info1['date'],
                y=info1['delay'],
                name='delay'
            )
            trace2 = go.Scatter(
                x=info2['date'],
                y=info2['count'],
                name='flights'
            )

            fig = make_subplots()
            fig.add_trace(trace1)
            fig.add_trace(trace2)

            #fig = px.line([info1,info2], x="date", y=["count","delay"])
            return fig
        else:
            return fig
    return fig


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
            # figure = px.line_polar(
            #     data,
            #     r= "ON_TIME_RATE",
            #     theta="DEPARTURE_TIME",
            #     line_close=True
            # )
            figure= px.sunburst(data,path=["TIME_SEGMENT","DEPARTURE_TIME"],
                                values="TOTAL", color_continuous_scale="RdBu",
                                color="ON_TIME_RATE",
                                color_continuous_midpoint=np.average(data["ON_TIME_RATE"],weights=data["TOTAL"])

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
        df["nums_ratio"] = df["nums"].map(lambda x: x * 100 / sum(destinations_num))
        # table_header = [
        #     html.Thead(html.Tr([html.Th("Destination"),html.Th("Flights_sum")]))
        # ]
        # table_body = [html.Tbody([html.Tr([html.Td(row["destination"]),html.Td(row["nums"])]) for idx, row in df.iterrows()])]
        total_flights = sum(destinations_num)

        def update_num_ratio(*args):

            y_nums_ratio = list(df["nums_ratio"])
            x = list(df["destination"])
            y_nums_ratio.reverse()
            x.reverse()

            # Creating two subplots
            fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                                shared_yaxes=False, vertical_spacing=0.01)

            fig.append_trace(go.Bar(
                x=y_nums_ratio,
                y=x,
                marker=dict(
                    color='rgba(67, 56, 209, 0.7)',
                    line=dict(
                        color='rgba(67, 56, 209, 1.0)',
                        width=1),
                ),
                name='Ratio of flights to hottest destination',
                orientation='h',
                width=0.3
            ), 1, 1)

            fig.update_layout(
                title='Ratio of flights to hottest destination and delay time distribution',
                yaxis=dict(
                    showgrid=False,
                    showline=False,
                    showticklabels=True,
                    domain=[0, 0.8],
                ),
                xaxis=dict(
                    zeroline=False,
                    showline=False,
                    showticklabels=False,
                    showgrid=True,
                    domain=[0, 0.22],
                ),
                showlegend=True,
                legend=dict(x=0.029, y=1.038, font_size=10),
                margin=dict(l=30, r=20, t=50, b=70),
                paper_bgcolor='rgb(255,255,255)',
                plot_bgcolor='rgb(255, 255, 255)',
            )

            annotations = []

            y_s = np.round(y_nums_ratio, decimals=2)

            # Adding labels
            for yd, xd in zip(y_s, x):

                # labeling the bar num ratio
                annotations.append(dict(xref='x1', yref='y1',
                                        y=xd, x=yd + 24,
                                        text=str(yd) + '%',
                                        font=dict(family='Arial', size=12,
                                                  color='rgb(67, 56, 209)'),
                                        showarrow=False))

            fig.update_layout(annotations=annotations)

            return fig


        obj = dbc.Card(children=[
            html.H6("Airport Name: {}".format(infos["AIRPORT"].values[0]), style={'fontFamily': 'Arial', 'color':'rgb(54, 76, 117)'}),
            html.H6("City Name: {}".format(infos["CITY"].values[0]), style={'fontFamily': 'Arial', 'color':'rgb(54, 76, 117)'}),
            html.H6("Total Flights of Today: {}".format(total_flights), style={'fontFamily': 'Arial',
                                                                               'color':'rgb(54, 76, 117)'}),
            #dbc.Table(table_header+table_body,bordered=True)
            dcc.Graph(figure=update_num_ratio())
            ]
        )
        return obj

if __name__ == '__main__':
    app.run_server(debug=True)

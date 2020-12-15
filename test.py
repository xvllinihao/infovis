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
numFlight = pd.read_csv("data/total.csv")
delay = pd.read_csv("data/delay.csv")
overview_destination = pd.read_json("data/overview_destinations.json")
detail_delay_information = pd.read_json("data/detail_delay_information.json")




location_dic = {}
for idx,row in airports_info.iterrows():
    location_dic[row["IATA_CODE"]] = {"lat":row["LATITUDE"], "lon":row["LONGITUDE"]}

tab1_content = dbc.Card(
            [
             dbc.CardBody(
                 children=[
                     # dcc.Checklist(
                     #     id="DOF",
                     #     options=[{"label": "# Total Flights", "value": "Total"},
                     #              {"label": "# Delayed Flights", "value": "Delayed"}
                     #              ],
                     #     value=["Total", "Delayed"],
                     #     style={'padding-left':'25%', 'padding-right':'25%'},
                     #     labelStyle={'display': 'inline',"padding": "5px"}
                     # ),
                     dcc.Graph(id="line-chart", style={"width":"100%","height":"100%"},
                               config={
                                   'displayModeBar': False,
                                   'displaylogo': False,
                                   'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian',
                                                              'hoverClosestCartesian', 'toggleSpikelines']
                               },
                               )
                 ]
             )],
            style={"width":"47.5rem", "height":"33rem"},
        )
tab2_content = dbc.Card(outline=False,children=[
    dbc.CardBody(
    dbc.Row(children=[
                dbc.Col(
                    children=[
                    dbc.Row(children=[
                        dbc.Col(
                        style={'padding-left':'2%', 'padding-right':'3%', 'padding-top':'0%'},
                        children=[
                        dcc.Dropdown(
                            id='date_menu',
                            options=[{'label': pd.to_datetime(timestamp).strftime('%Y.%m.%d'), 'value': timestamp} for
                                     timestamp in airports["DATE"].unique()],
                            #placeholder="select a date to find detailed information"
                            value=airports["DATE"].unique()[0],
                        )],width=8
                        ),
                    ]
                    ),
                    dbc.Col(
                            id='info_box'
                    ), ]),
            ]))
    ],style={"width":"47.5rem", "height":"33rem"},)
tab_height="1vh"
tabs = dbc.Tabs(
    #style={"position":"relative", "left":"200px"},
    children=[
    dbc.Tab(tab1_content, label="Overview", tab_style={"height":"50px", "background-color":"white"},label_style={"height":"50px","background-color":"#f7f7f7"}),
    dbc.Tab(tab2_content, label="More Info", tab_style={"height":"50px", "background-color":"white"},label_style={"height":"50px","background-color":"#f7f7f7"}),])

app.title = "Traveling in Christmas"
app.layout = html.Div(children=[
    dbc.Card(children=[
        html.H1(children='Traveling in Christmas',style={'padding-left':'35%', 'padding-right':'25%'}),
        dbc.Row(
            children=[
                dbc.Col(
                    style={'padding-left':'3%', 'padding-right':'3%', 'padding-top':'1%'},
                    children=[
                    dbc.Card(
                        style={"width":"35rem"},
                        children=[
                        dbc.CardHeader("Map"),
                        dbc.CardBody(
                            children=[
                            dbc.Row(children=[
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='airport_menu',
                                        options=[{'label': IATA, 'value': IATA} for IATA in airports_info["IATA_CODE"]],
                                        placeholder="select an airport to find detail information"
                                    ),
                                    width=8
                                    ),
                            ]
                       ),
                        dcc.Graph(id="map",clear_on_unhover=True,style={"width":"100%", "height":"100%"},
                                  config={
                                      'displayModeBar': False,
                                      'displaylogo': False,
                                      'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian',
                                                                 'hoverClosestCartesian', 'toggleSpikelines']
                                  },
                                  ),
                        ])
                    ])
                     ]),
                dbc.Col(
                    style={'padding-left':'1%', 'padding-right':'3%', 'padding-top':'1%', "position":"relative", "right":"115px", "width":"100px"},
                    children=[tabs]
                )
            ]
        ),
    ]
    )
]
)

@app.callback(
    Output('airport_menu','value'),
    [Input('map','selectedData')],
)
def update_airport_menu(selectedData):
    airport = None
    if selectedData:
        point_dict = selectedData["points"][0]
        airport = point_dict['hovertext']
    return airport


@app.callback(
    Output('map','figure'),
    [Input('map','selectedData'),Input('date_menu','value'), Input("map","hoverData"),Input("airport_menu","value")],
)
def update_click_map(selectedData,date,hoverData,inputData):
    """
    单击地图上的点选定要看的机场，双击取消选定，有时候会有bug，后面研究一哈
    :param selectedData:
    :param date:
    :param hoverData:
    :return:
    """
    timestamp = pd.to_datetime(date) if date else 0
    fig = px.scatter_geo(
        airports_info,
        scope="usa",
        lat=airports_info["LATITUDE"],
        lon=airports_info["LONGITUDE"],
        hover_name=airports_info["IATA_CODE"],
        )

    fig.update_layout(clickmode="event+select")
    fig.update_layout(hovermode="closest")
    fig.update_layout(
        margin=dict(l=5, r=0, t=20, b=20),
    )
    if inputData:
        origin_lon = location_dic[inputData]['lon']
        origin_lat = location_dic[inputData]['lat']
        airport = inputData

        infos = airports[(airports["ORIGIN_AIRPORT"]==airport) & (airports["DATE"]==timestamp)] if timestamp!=0 \
            else overview_destination[overview_destination["ORIGIN_AIRPORT"]==airport]
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
        fig.update_layout(
            margin=dict(l=0, r=0, t=20, b=20),
        )

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



    if selectedData and inputData:
        point_dict = selectedData["points"][0]
        origin_lon = point_dict['lon']
        origin_lat = point_dict['lat']
        airport = point_dict['hovertext']

        infos = airports[(airports["ORIGIN_AIRPORT"]==airport) & (airports["DATE"]==timestamp)] if timestamp!=0 \
            else overview_destination[overview_destination["ORIGIN_AIRPORT"]==airport]
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
        fig.update_layout(
            margin=dict(l=0, r=0, t=20, b=20),
        )

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

        infos = airports[(airports["ORIGIN_AIRPORT"] == airport) & (airports["DATE"] == timestamp)] if timestamp != 0 \
            else overview_destination[overview_destination["ORIGIN_AIRPORT"] == airport]
        #infos = airports[(airports["ORIGIN_AIRPORT"]==airport) & (airports["DATE"]==timestamp)]
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
        # fig.update_layout(clear_on_unhover=True)
        return fig
    else:
        return fig

@app.callback(
    Output('info_box','children'),
    [Input('map','selectedData'),Input('date_menu','value'),Input('airport_menu','value')]
)
def update_infobox(selectedData,date, inputData):
    if date:
        timestamp = pd.to_datetime(date)
        data = on_time_list[on_time_list["DATE"]==timestamp]
        #我处理的时候是int型的，会默认转成度数，要换成str才能24等分
        time_list = data["DEPARTURE_TIME"].tolist()
        for i in range(len(time_list)):
            time_list[i] = str(time_list[i])+":00"
        data["DEPARTURE_TIME"] = time_list

        #没有选定数据的时候就显示雷达图
        if not inputData:
            fig = px.sunburst(data,path=["TIME_SEGMENT","DEPARTURE_TIME"],
                                    values="TOTAL", color_continuous_scale="RdBu",
                                    color="ON_TIME_RATE",
                                    color_continuous_midpoint=np.average(data["ON_TIME_RATE"],weights=data["TOTAL"]),

                                    )
            # fig2 = go.Figure(go.Sunburst(
            #     labels=fig['data'][0]['labels'].tolist(),
            #     parents=fig['data'][0]['parents'].tolist(),
            #     values=fig['data'][0]['values'].tolist(),
            #     sort=True
            # ))
            fig.update_layout(
                margin=dict(l=0, r=0, t=25, b=20),
            )
            obj = dcc.Graph(
                # figure = px.line_polar(
                #     data,
                #     r= "ON_TIME_RATE",
                #     theta="DEPARTURE_TIME",
                #     line_close=True
                # )
                # figure= px.sunburst(data,path=["TIME_SEGMENT","DEPARTURE_TIME"],
                #                     values="TOTAL", color_continuous_scale="RdBu",
                #                     color="ON_TIME_RATE",
                #                     color_continuous_midpoint=np.average(data["ON_TIME_RATE"],weights=data["TOTAL"])
                #
                #                     )
                figure=fig,
                style={"width": "100%", "height": "100%", "position":"relative"},
                config = {
                         'displayModeBar': False,
                         'displaylogo': False,
                         'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian',
                                                    'hoverClosestCartesian', 'toggleSpikelines']
                     },
            )
            return obj


        #有选定数据就显示卡片
        elif inputData:
            point_dict = selectedData["points"][0] if selectedData else None
            airport = inputData if inputData else point_dict["hovertext"]
            infos = airports_info[airports_info["IATA_CODE"]==airport]
            detailed_infos = airports[(airports["ORIGIN_AIRPORT"] == airport) & (airports["DATE"] == timestamp)]
            destinations = detailed_infos["DESTINATION_AIRPORT"].tolist()[0] if detailed_infos["DESTINATION_AIRPORT"].tolist() else []
            destinations_num = detailed_infos["FLIGHT_SUM"].tolist()[0] if detailed_infos["FLIGHT_SUM"].tolist() else []
            df = pd.DataFrame()
            df["destination"] = destinations
            df["nums"] = destinations_num
            df = df.nlargest(5,"nums")
            total_flights = sum(destinations_num)

            data = []
            name_list = ["on time","0≤delay<30","30≤delay<60","delay≥60"]

            for i in range(0, 4):
                y = []
                for des in df["destination"]:
                    tmp = detail_delay_information[(detail_delay_information["ORIGIN_AIRPORT"]==airport) &
                                                   (detail_delay_information["DESTINATION_AIRPORT"]==des) &
                                                   (detail_delay_information["DELAY_SEG"]==float(i)) &
                                                   (detail_delay_information["DATE"]==timestamp)
                                                   ]
                    tmplist = tmp["DEPARTURE_DELAY"].tolist()
                    y.append(len(tmplist[0]) if tmplist else 0)
                data.append(go.Bar(
                    name=name_list[i],
                    y=df["destination"],
                    x=y,
                    orientation = 'h'
                ))

            fig = go.Figure(data=data)
            fig.update_layout(barmode='stack')
            fig.update_layout(
                margin=dict(l=8, r=0, t=20, b=20),
                autosize=False,
                width=350,
                height=300,
            )
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))

            # df["nums_ratio"] = df["nums"].map(lambda x: x * 100 / sum(destinations_num))
            # # table_header = [
            # #     html.Thead(html.Tr([html.Th("Destination"),html.Th("Flights_sum")]))
            # # ]
            # # table_body = [html.Tbody([html.Tr([html.Td(row["destination"]),html.Td(row["nums"])]) for idx, row in df.iterrows()])]
            #
            # def update_num_ratio(*args):
            #
            #     y_nums_ratio = list(df["nums_ratio"])
            #     x = list(df["destination"])
            #     y_nums_ratio.reverse()
            #     x.reverse()
            #
            #     # Creating two subplots
            #     fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
            #                         shared_yaxes=False, vertical_spacing=0.01)
            #
            #     fig.append_trace(go.Bar(
            #         x=y_nums_ratio,
            #         y=x,
            #         marker=dict(
            #             color='rgba(67, 56, 209, 0.7)',
            #             line=dict(
            #                 color='rgba(67, 56, 209, 1.0)',
            #                 width=1),
            #         ),
            #         name='Ratio of flights to hottest destination',
            #         orientation='h',
            #         width=0.3
            #     ), 1, 1)
            #
            #     fig.update_layout(
            #         title='Ratio of flights to hottest destination and delay time distribution',
            #         yaxis=dict(
            #             showgrid=False,
            #             showline=False,
            #             showticklabels=True,
            #             domain=[0, 0.8],
            #         ),
            #         xaxis=dict(
            #             zeroline=False,
            #             showline=False,
            #             showticklabels=False,
            #             showgrid=True,
            #             domain=[0, 0.22],
            #         ),
            #         showlegend=True,
            #         legend=dict(x=0.029, y=1.038, font_size=10),
            #         margin=dict(l=30, r=20, t=50, b=70),
            #         paper_bgcolor='rgb(255,255,255)',
            #         plot_bgcolor='rgb(255, 255, 255)',
            #     )
            #
            #     annotations = []
            #
            #     y_s = np.round(y_nums_ratio, decimals=2)
            #
            #     # Adding labels
            #     for yd, xd in zip(y_s, x):
            #
            #         # labeling the bar num ratio
            #         annotations.append(dict(xref='x1', yref='y1',
            #                                 y=xd, x=yd + 24,
            #                                 text=str(yd) + '%',
            #                                 font=dict(family='Arial', size=12,
            #                                           color='rgb(67, 56, 209)'),
            #                                 showarrow=False))
            #
            #     fig.update_layout(annotations=annotations)
            #
            #     return fig



            obj = dbc.Row(
                children=[
                dbc.Row(
                    style={'padding-left': '3%', 'padding-right': '3%', 'padding-top': '1%', "position": "relative"},
                    children=[
                        html.P(["Airport Name: {}\n".format(infos["AIRPORT"].values[0]), html.Br(), "City Name: {}\n".format(infos["CITY"].values[0]),
                                html.Br(), "Total Flights of Today: {}\n".format(total_flights)], style={'fontFamily': 'Arial', 'color':'rgb(54, 76, 117)'})]
                ),
                dbc.Row(
                    #style={"width": "100%", "height": "100%", "position": "relative"},
                    children=[
                #dbc.Table(table_header+table_body,bordered=True)
                dbc.Col([dcc.Graph(figure=fig,clear_on_unhover=True,id="stacked_bar",
                        config = {
                         'displayModeBar': False,
                         'displaylogo': False,
                         'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian',
                                                    'hoverClosestCartesian', 'toggleSpikelines']
                     },)],style={'padding-left': '3%', 'padding-right': '0%', 'padding-top': '1%', "position": "relative"},
                        width={"size":410}),
                dbc.Col(
                    [dcc.Graph(id="scatter",
                               style={"position": "relative", "right": "0px","display": "block",},
                        config = {
                         'displayModeBar': False,
                         'displaylogo': False,
                         'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian',
                                                    'hoverClosestCartesian', 'toggleSpikelines']
                     },)],style={'padding-left': '3%', 'padding-right': '0%', 'padding-top': '5.6%', "position": "relative", "right":"0px"},
                    width={"size":270})]
            ),
            ]
            )
            return obj
    # else:
    #     obj = dbc.Card(
    #         [dbc.CardHeader("Overview"),
    #          dbc.CardBody(
    #              children=[
    #                  # dcc.Checklist(
    #                  #     id="DOF",
    #                  #     options=[{"label": "# Total Flights", "value": "Total"},
    #                  #              {"label": "# Delayed Flights", "value": "Delayed"}
    #                  #              ],
    #                  #     value=["Total", "Delayed"],
    #                  #     style={'padding-left':'25%', 'padding-right':'25%'},
    #                  #     labelStyle={'display': 'inline',"padding": "5px"}
    #                  # ),
    #                  dcc.Graph(id="line-chart")
    #              ]
    #          )],
    #
    #     )
    #     return obj
@app.callback(
    Output('line-chart','figure'),
    #[Input('DOF','value'), Input("map","selectedData"),Input('airport_menu','value')],
    [Input("map","selectedData"),Input('airport_menu','value')],
)
def update_line_chart(selectedData, inputData):
    total_flight = numFlight.groupby(["date"])["count"].sum().reset_index()
    total_delay = delay.groupby(["date"])["count"].sum().reset_index()
    fig = go.Figure()
    #if "Total" in selectedDOF:
    figTitle = "Flight Statistics Nationwide"
    fig.add_trace(go.Scatter(x=total_flight["date"],y=total_flight["count"],name="Total"))
    #if "Delayed" in selectedDOF:
        #figTitle = "Flight Statistics Nationwide"
    fig.add_trace(go.Scatter(x=total_delay["date"], y=total_delay["count"],name="Delayed"))

    if inputData:
        airport = inputData
        figTitle = "Flight Statistics in " + airport
        # if selectedDOF == ["Total"]:
        #     info = numFlight[(numFlight["ORIGIN_AIRPORT"]==airport)]
        #     fig = px.line(info, x="date", y="count")
        #     fig.update_layout(title=figTitle,title_x=0.47,title_y=0.85)
        #     return fig
        # elif selectedDOF == ["Delayed"]:
        #     info = delay[(delay["ORIGIN_AIRPORT"]==airport)]
        #     fig = px.line(info, x="date", y="count")
        #     fig.update_layout(title=figTitle,title_x=0.47,title_y=0.85)
        #     return fig
        # elif (selectedDOF == ["Total","Delayed"] or selectedDOF == ["Delayed","Total"]):
        info1 = delay[(delay["ORIGIN_AIRPORT"] == airport)]
        info2 = numFlight[(numFlight["ORIGIN_AIRPORT"] == airport)]
        trace1 = go.Scatter(
                x=info1['date'],
                y=info1['count'],
                name='Delayed'
        )
        trace2 = go.Scatter(
                x=info2['date'],
                y=info2['count'],
                name='Total',
        )

        fig = make_subplots()
        fig.update_layout(title=figTitle,title_x=0.47,title_y=0.85)
        fig.add_trace(trace1)
        fig.add_trace(trace2)

            #fig = px.line([info1,info2], x="date", y=["count","delay"])
        return fig

    if selectedData and inputData:
        airport = selectedData["points"][0]['hovertext']
        # if selectedDOF == ["flights"]:
        #     info = numFlight[(numFlight["ORIGIN_AIRPORT"]==airport)]
        #     fig = px.line(info, x="date", y="count")
        #     return fig
        # elif selectedDOF == ["delay"]:
        #     info = delay[(delay["ORIGIN_AIRPORT"]==airport)]
        #     fig = px.line(info, x="date", y="delay")
        #     return fig
        # elif (selectedDOF == ["flights","delay"] or selectedDOF == ["delay","flights"]):
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
        # else:
        #     return fig
    fig.update_layout(title=figTitle,title_x=0.47,title_y=0.85)
    return fig

@app.callback(
    Output("scatter","figure"),
    Input("stacked_bar","hoverData"),
    Input('airport_menu','value'),
    Input('date_menu','value')
)
def update_scatter(hoverData,inputData,date):
    timestamp =pd.to_datetime(date)
    airport = inputData
    infos = airports_info[airports_info["IATA_CODE"] == airport]
    detailed_infos = airports[(airports["ORIGIN_AIRPORT"] == airport) & (airports["DATE"] == timestamp)]
    destinations = detailed_infos["DESTINATION_AIRPORT"].tolist()[0] if detailed_infos[
        "DESTINATION_AIRPORT"].tolist() else []
    destinations_num = detailed_infos["FLIGHT_SUM"].tolist()[0] if detailed_infos["FLIGHT_SUM"].tolist() else []
    df = pd.DataFrame()
    df["destination"] = destinations
    df["nums"] = destinations_num
    df = df.nlargest(5, "nums")
    #时间是x轴，delay是y轴，时间是小数形式，我已经做了转化，比如6:30就是6.5小时
    delays = []
    times = []
    for i in range(0, 4):
        for des in df["destination"]:
            tmp = detail_delay_information[(detail_delay_information["ORIGIN_AIRPORT"] == airport) &
                                           (detail_delay_information["DESTINATION_AIRPORT"] == des) &
                                           (detail_delay_information["DELAY_SEG"] == float(i)) &
                                           (detail_delay_information["DATE"] == timestamp)
                                           ]
            delay_list = tmp["DEPARTURE_DELAY"].tolist()
            time_list = tmp["DEPARTURE_TIME"].tolist()
            delays +=delay_list[0] if delay_list else []
            times +=time_list[0] if time_list else []
    if not times and not delays:
        fig = px.line()
    else:
        fig = px.scatter(x=times,y=delays)




    #当有hover的时候就只展示选定的延误时间分布
    if hoverData:
        point_dict = hoverData["points"][0]
        curveNumber = point_dict["curveNumber"]
        des = point_dict["label"]
        infos = detail_delay_information[(detail_delay_information["ORIGIN_AIRPORT"]==airport) &
                                     (detail_delay_information["DESTINATION_AIRPORT"]==des) &
                                     (detail_delay_information["DELAY_SEG"]==curveNumber) &
                                     (detail_delay_information["DATE"] == timestamp)
                                      ]
        x = infos["DEPARTURE_TIME"].tolist()[0]
        y = infos["DEPARTURE_DELAY"].tolist()[0]
        fig = px.scatter(x=x,y=y)
        fig.update_layout(
            margin=dict(l=0, r=0, t=20, b=20),
            autosize=False,
            width=315,
            height=290,
        )
        return fig
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=20),
        autosize=False,
        width=315,
        height=290,
    )
    return fig


if __name__ == '__main__':
    app.config['suppress_callback_exceptions'] = True
    app.run_server(debug=True)

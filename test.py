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
from datetime import datetime

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

pd.set_option("max_columns", None)
airports = pd.read_json("data/processed_airports.json")
airports_info = pd.read_csv("data/airports.csv")
on_time_list = pd.read_json("data/on_time_list.json")
numFlight = pd.read_csv("data/total.csv")
delay = pd.read_csv("data/delay.csv")
overview_destination = pd.read_json("data/overview_destinations.json")
detail_delay_information = pd.read_json("data/detail_delay_information.json")
airports_info["COLOR_MAP"]="#525252"
px.colors.sequential.Plasma = ["#fff5f0", "#fee0d2", "#fcbba1", "#a50f15", "#67000d"]



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
            style={"width":"100%", "height":"33rem"},
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
                            id='info_box',style={'padding-left':'1%', 'padding-right':'3%', 'padding-top':'1%'},
                    ), ]),
            ]))
    ],style={"width":"100%", "height":"33rem"},)
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
                        style={"width":"100%"},
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
                    style={'padding-left':'3%', 'padding-right':'3%', 'padding-top':'1%', "position":"relative", "right":"3%", "width":"100%"},
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
        color="COLOR_MAP",
        color_discrete_map="identity"
        )

    fig.update_layout(hovermode="closest",
                      margin=dict(l=5, r=0, t=20, b=20),
                      clickmode="event+select",
                      template='ggplot2')
    if inputData:
        origin_lon = location_dic[inputData]['lon']
        origin_lat = location_dic[inputData]['lat']
        airport = inputData

        infos = airports[(airports["ORIGIN_AIRPORT"]==airport) & (airports["DATE"]==timestamp)] if timestamp!=0 \
            else overview_destination[overview_destination["ORIGIN_AIRPORT"]==airport]
        destinations = infos["DESTINATION_AIRPORT"].tolist()[0] if infos["DESTINATION_AIRPORT"].tolist() else []
        points = airports_info[airports_info["IATA_CODE"].isin(destinations) | (airports_info["IATA_CODE"]==airport)]
        points["COLOR_MAP"] = "#525252"
        fig = px.scatter_geo(
            airports_info,
            scope="usa",
            lat=points["LATITUDE"],
            lon=points["LONGITUDE"],
            hover_name=points["IATA_CODE"],
            hover_data=None,
            color=points["COLOR_MAP"],
            color_discrete_map="identity"
        )

        fig.update_layout(clickmode="event+select",
                          margin=dict(l=0, r=0, t=20, b=20),
                          template="ggplot2")

        for des in destinations:
            fig.add_trace(
                go.Scattergeo(
                    lon=[origin_lon, location_dic[des]["lon"]],
                    lat=[origin_lat, location_dic[des]["lat"]],
                    mode="lines",
                    line = dict(width=1,color='#cb181d'),
                    marker=dict(color='#cb181d'),
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
        points["COLOR_MAP"] = "#525252"
        fig = px.scatter_geo(
            airports_info,
            scope="usa",
            lat=points["LATITUDE"],
            lon=points["LONGITUDE"],
            hover_name=points["IATA_CODE"],
            hover_data=None,
            color=points["COLOR_MAP"],
            color_discrete_map="identity"
        )

        fig.update_layout(clickmode="event+select")
        fig.update_layout(
            margin=dict(l=0, r=0, t=20, b=20),
            template="ggplot2"
        )

        for des in destinations:
            fig.add_trace(
                go.Scattergeo(
                    lon=[origin_lon, location_dic[des]["lon"]],
                    lat=[origin_lat, location_dic[des]["lat"]],
                    mode="lines",
                    line = dict(width=1,color='#cb181d'),
                    marker=dict(color='#cb181d'),
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
                    line = dict(width=1,color='#cb181d'),
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
        print(timestamp.month)
        data = on_time_list[on_time_list["DATE"]==timestamp]
        #我处理的时候是int型的，会默认转成度数，要换成str才能24等分
        time_list = data["DEPARTURE_TIME"].tolist()
        for i in range(len(time_list)):
            time_list[i] = str(time_list[i])+":00"
        data["DEPARTURE_TIME"] = time_list

        #没有选定数据的时候就显示雷达图
        if not inputData:
            fig = px.sunburst(data,path=["TIME_SEGMENT","DEPARTURE_TIME"],
                                    values="TOTAL", color_continuous_scale="Plasma",
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
            fig.update_layout(title="Departure Delay Number & Length Distribution at {}-{} Nationwide".format(timestamp.month, timestamp.day))
            obj = dcc.Graph(
                figure=fig,
                style={"width": "90%", "height": "90%", "position":"relative","padding-top":"2%"},
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
            name_list = ["on time","0≤delay<30", "30≤delay<60", "delay≥60"]
            colors=["#fdd0a2","#fb6a4a", "#a50f15", "#67000d"]
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
                    orientation = 'h',
                    marker_color=colors[i],
                    opacity=0.8,
                    width=0.3
                ))


            fig = go.Figure(data=data)
            fig.update_layout(barmode='stack', template="simple_white")
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                # autosize=False,
                # width=700,
                # height=200,
                bargap=0.4,
                xaxis=dict(
                            zeroline=False,
                            showline=False,
                            color="#525252",
                            showticklabels=True,
                            showgrid=True,
                            domain=[0, 0.8],
                        ),
                yaxis=dict(
                    color = "#525252",
                    domain=[0, 0.9],
                    showline=False
                ),
            )
            fig.update_layout(legend=dict(
                orientation="h",
                # yanchor="bottom",
                # y=0.98,
                # xanchor="right",
                # x=0.05,
            ))


            obj = dbc.Row(
                children=[
                dbc.Row(
                    style={'padding-left': '3%', 'padding-right': '3%', 'padding-top': '1%', "position": "relative"},
                    children=[
                        html.P(["Airport Name: {}\n".format(infos["AIRPORT"].values[0]), html.Br(), "City Name: {}\n".format(infos["CITY"].values[0]),
                                html.Br(), "Total Flights of Today: {}\n".format(total_flights)], style={'fontFamily': 'Arial', 'color':'#525252'})]
                ),
                dbc.Row([html.P(["Departure Delay Length Distribution of Flights From {} To Hottest Destinations".format(airport)],style={"text-align":"center","position":"relative","padding-left":"8%","padding-right":"8%","width":"100%","height":"100%"})]
                        ,style={"width": "100%",'padding-bottom': '0%',"height":"27px"}
                        ),
                dbc.Row(
                    style={"width": "100%", "height": "350px", "position": "relative"},
                    children=[
                #dbc.Table(table_header+table_body,bordered=True)
                dbc.Col([dcc.Graph(figure=fig,clear_on_unhover=True,id="stacked_bar",
                                   style={
                                          "position": "relative", "height": "100%", "width": "100%"},
                        config = {
                         'displayModeBar': False,
                         'displaylogo': False,
                         'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian',
                                                    'hoverClosestCartesian', 'toggleSpikelines']
                     },)],style={'padding-left': '3%', 'padding-right': '0%', "position": "relative","height":"90%","width":"50%"},
                        #width={"size":"100%"}
                        ),#410
                dbc.Col(
                    [dcc.Graph(id="scatter",
                               style={"position": "relative", "height": "90%", "width": "100%"},
                        config = {
                         'displayModeBar': False,
                         'displaylogo': False,
                         'modeBarButtonsToRemove': ['zoom2d', 'hoverCompareCartesian',
                                                    'hoverClosestCartesian', 'toggleSpikelines']
                     },)],style={'padding-left': '0%', 'padding-right': '0%','padding-bottom': '3%', "position": "relative","height":"100%","width":"50%" },
                    #width={"size":"100%"}
                )]#270
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
    fig.add_trace(go.Scatter(x=total_flight["date"],y=total_flight["count"],name="Total", line=dict(color="#525252")))
    #if "Delayed" in selectedDOF:
        #figTitle = "Flight Statistics Nationwide"
    fig.add_trace(go.Scatter(x=total_delay["date"], y=total_delay["count"],name="Delayed", line=dict(color="#cb181d")))


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
                name='Delayed',
                line=dict(color="#cb181d")

        )
        trace2 = go.Scatter(
                x=info2['date'],
                y=info2['count'],
                name='Total',
                line=dict(color="#525252")
        )

        fig = make_subplots()
        fig.update_layout(title=figTitle,title_x=0.47,title_y=0.85)
        fig.add_trace(trace1)
        fig.add_trace(trace2)
        fig.update_layout(template="ggplot2")

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
                name='delay',
                line=dict(color="#cb181d")
        )
        trace2 = go.Scatter(
                x=info2['date'],
                y=info2['count'],
                name='flights',
                line=dict(color="#525252")
        )

        fig = make_subplots()
        fig.add_trace(trace1)
        fig.add_trace(trace2)

            #fig = px.line([info1,info2], x="date", y=["count","delay"])
        return fig
        # else:
        #     return fig
    fig.update_layout(title=figTitle,title_x=0.47,title_y=0.85, template="ggplot2")
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
    color_seg = []
    for i in range(0, 4):
        for des in df["destination"]:
            tmp = detail_delay_information[(detail_delay_information["ORIGIN_AIRPORT"] == airport) &
                                           (detail_delay_information["DESTINATION_AIRPORT"] == des) &
                                           (detail_delay_information["DELAY_SEG"] == float(i)) &
                                           (detail_delay_information["DATE"] == timestamp)
                                           ]

            tmp["COLOR_STR"] = 0
            tmp.loc[tmp["DELAY_SEG"] == 0, "COLOR_STR"] = "#fdd0a2"
            tmp.loc[tmp["DELAY_SEG"] == 1, "COLOR_STR"] = "#fb6a4a"
            tmp.loc[tmp["DELAY_SEG"] == 2, "COLOR_STR"] = "#a50f15"
            tmp.loc[tmp["DELAY_SEG"] == 3, "COLOR_STR"] = "#67000d"

            delay_list = tmp["DEPARTURE_DELAY"].tolist()
            time_list = tmp["DEPARTURE_TIME"].tolist()
            color_list = tmp["COLOR_STR"].tolist()
            delays += delay_list[0] if delay_list else []
            times += time_list[0] if time_list else []
            color_seg += color_list*len(delay_list[0]) if color_list else []

    fig = px.scatter(x=times, y=delays, color=color_seg, color_discrete_map="identity")


    fig.update_layout(
       margin=dict(l=0, r=0, t=20, b=5),
         showlegend=False,
            xaxis=dict(
            title="time",
            rangemode="tozero",
            showline=True,
            color="#525252",
            showticklabels=True,
            showgrid=False,
            fixedrange=True,
            tickmode="array",
            range=[0,25],
            tickvals=(0,3,6,9,12,15,18,21,24),
            ticktext=('0:00','3:00','6:00','9:00','12:00','15:00', "18:00", "21:00", "24:00"),
            zeroline=True,

            ),
        yaxis=dict(
            title="delay length (min)",
            color="#525252",
            showticklabels=True,
            showgrid=True,
            showline=False,
            ticks="outside",

        ),
    )
    # 当有hover的时候就只展示选定的延误时间分布
    if hoverData:
        point_dict = hoverData["points"][0]
        curveNumber = point_dict["curveNumber"]
        des = point_dict["label"]
        delaysl = []
        timesl = []
        color_s=[]
        for i in range(0, 4):
            infos = detail_delay_information[(detail_delay_information["ORIGIN_AIRPORT"] == airport) &
                                               (detail_delay_information["DESTINATION_AIRPORT"] == des) &
                                               (detail_delay_information["DELAY_SEG"] == float(i)) &
                                               (detail_delay_information["DATE"] == timestamp)
                                               ]

            infos["COLOR_STR"] = 0

            if curveNumber == 0:
                infos.loc[(infos["DELAY_SEG"] == curveNumber), "COLOR_STR"] = "#fdd0a2"
                infos.loc[(infos["DELAY_SEG"] == 1), "COLOR_STR"] = "#969696"
                infos.loc[infos["DELAY_SEG"] == 2, "COLOR_STR"] = "#969696"
                infos.loc[infos["DELAY_SEG"] == 3, "COLOR_STR"] = "#969696"
            if curveNumber == 1:
                infos.loc[(infos["DELAY_SEG"] == 0), "COLOR_STR"] = "#969696"
                infos.loc[(infos["DELAY_SEG"] == curveNumber), "COLOR_STR"] = "#fb6a4a"
                infos.loc[infos["DELAY_SEG"] == 2, "COLOR_STR"] = "#969696"
                infos.loc[infos["DELAY_SEG"] == 3, "COLOR_STR"] = "#969696"
            if curveNumber == 2:
                infos.loc[(infos["DELAY_SEG"] == 0), "COLOR_STR"] = "#969696"
                infos.loc[(infos["DELAY_SEG"] == 1), "COLOR_STR"] = "#969696"
                infos.loc[infos["DELAY_SEG"] == curveNumber, "COLOR_STR"] = "#a50f15"
                infos.loc[infos["DELAY_SEG"] == 3, "COLOR_STR"] = "#969696"
            if curveNumber == 3:
                infos.loc[(infos["DELAY_SEG"] == 0), "COLOR_STR"] = "#969696"
                infos.loc[(infos["DELAY_SEG"] == 1), "COLOR_STR"] = "#969696"
                infos.loc[infos["DELAY_SEG"] == 2, "COLOR_STR"] = "#969696"
                infos.loc[infos["DELAY_SEG"] == curveNumber, "COLOR_STR"] = "#67000d"

            # x = infos["DEPARTURE_TIME"].tolist()[0]
            # y = infos["DEPARTURE_DELAY"].tolist()[0]
            delay_l = infos["DEPARTURE_DELAY"].tolist()
            time_l = infos["DEPARTURE_TIME"].tolist()
            color_l = infos["COLOR_STR"].tolist()
            delaysl += delay_l[0] if delay_l else []
            timesl += time_l[0] if time_l else []
            color_s += color_l * len(delay_l[0]) if color_l else []
        # fig = px.scatter(x=x,y=y)
        # fig.update_layout(
        #     margin=dict(l=0, r=0, t=20, b=20),
        #     template="simple_white"
        #     # autosize=False,
        #     # width=315,
        #     # height=290,
        # )


        fig=px.scatter(x=timesl, y=delaysl, color=color_s, color_discrete_map="identity")
        fig.update_layout(
            template="simple_white",
            margin=dict(l=0, r=0, t=60, b=5),
            showlegend=False,
            xaxis=dict(
                title="time per day",
                rangemode="tozero",
                showline=True,
                color="#525252",
                showticklabels=True,
                showgrid=False,
                fixedrange=True,
                tickmode="array",
                range=[0,25],
                tickvals=(0, 3, 6, 9, 12, 15, 18, 21, 24),
                ticktext=('0:00', '3:00', '6:00', '9:00', '12:00', '15:00', "18:00", "21:00", "24:00"),
                zeroline=True
            ),
            yaxis=dict(
                title="delay time",
                color="#525252",
                showticklabels=True,
                showgrid=True,
                zeroline=False,
                showline=False
            ),
        )

        return fig
    fig.update_layout(
        template="simple_white"
        # autosize=False,
        # width=315,
        # height=290,
    )
    return fig


if __name__ == '__main__':
    app.config['suppress_callback_exceptions'] = True
    app.run_server(debug=True, host="127.0.0.1")

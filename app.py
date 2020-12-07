'''

The modification of this file is as below:

1. change the dbc.themes to light bgcolor,
since it's nicer to put light bgcolor on the paper;
I use theme_color= "#002d55" as the main color for boxplot.

2. The pre-processing procedure of this file has been moved to app_preprocess.py,
the relevant variables needed for this file are imported.

3. Main modification is focused on update_delays();
I divided the delay time into short delay(less than 45min) and long delay(more than 45min, less than 180min).
The upper percentile interval line plot shows the long delay, for each long delay point,
it shows what the percentile of this point is in the whole delay time distribution of this airline in one day;
This is useful because, let's say, for one airline the long delay interval is [0.6-0.9], for another is [0.9-1.0];
This indicates the former airline has more extremely long delay time(more than 180min),
the latter airline has the longest delay which is only 180min.

The lower box plot shows the short delay.

The arrival delay and the departure delay are grouped in parallel, click one, another becomes transparent gray.

4. For now, the airline map and the airport map are commented out;
You can modify the codes when you start.

5. hoverinfo of the boxplot is not modified yet, I will figure it out later.

'''



import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash import callback_context
from dash.dependencies import Output, Input
from app_preprocess import flights_per_day, airlines, origin, destination
import numpy as np
import ast
import plotly.express as px

externel_stylesheets = [dbc.themes.LUMEN]
app = dash.Dash(__name__, external_stylesheets=externel_stylesheets)
theme_color = "#002d55"  # set the deep blue as theme color for text and plots

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

# read the two binning files processed in the app_preprocess.py
arrival_delays = pd.read_csv('data/arrival_binning_trans.csv',
                             index_col=0, parse_dates=['DATE'],
                             dtype={'ARRIVAL_DELAY': object,
                                    'ARRIVAL_DELAY_OUTLIER': object,
                                    'ARRIVAL_DELAY_MIN': np.float,
                                    'ARRIVAL_DELAY_MAX': np.float,
                                    'ARRIVAL_DELAY_WITHOUT_OUTLIER': object,
                                    'ARRIVAL_TRANS_OUTLIER': object})
departure_delays = pd.read_csv('data/departure_binning_trans.csv', index_col=0,
                               parse_dates=['DATE'],
                               dtype={'DEPARTURE_DELAY': object,
                                      'DEPARTURE_DELAY_OUTLIER': object,
                                      'DEPARTURE_DELAY_MIN': np.float,
                                      'DEPARTURE_DELAY_MAX': np.float,
                                      'DEPARTURE_DELAY_WITHOUT_OUTLIER': object,
                                      'DEPARTURE_TRANS_OUTLIER': object})

def get_flights_figure():
    flights_figure = go.Figure()
    flights_figure.add_trace(go.Scatter(
        x=flights_per_day["DATE"],
        y=flights_per_day["SUM"],
        mode="lines+markers",

    ))
    flights_figure.update_layout(
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin
            autoexpand=True
        ),
        paper_bgcolor='#204051',
        plot_bgcolor='#204051'
    )
    return flights_figure


app.layout = html.Div(children=[
    dbc.Container(children=[
        dbc.Card(children=
        dbc.Row([
            dbc.Col(children=[
                dbc.Badge("AIRLINE", color="info", className="mr-1"),
                dbc.ButtonGroup(
                    [dbc.Button(airline, id=airline, outline=False, color=theme_color, className="mr-1") for airline in
                     airlines["IATA_CODE"]],
                    size="md",
                    id="airline_input",
                    vertical=True
                )], width=1),
            dbc.Col(children=[
                html.H1("Flight map", style={'fontFamily': 'sans-serif'}),
                dcc.Graph(
                    id="flight_map",
                )], width=5),
            dbc.Col(children=[
                              dbc.Card(children=[
                                  dbc.FormGroup(
                                      [
                                          dbc.RadioItems(
                                              options=[
                                                  {"label": "ARRIVAL_DELAY", "value": "arrival"},
                                                  {"label": "DEPARTURE_DELAY", "value": "departure"}
                                              ],
                                              value="arrival",
                                              id="arrival_or_departure",
                                              labelCheckedStyle={"color": theme_color},  # change the theme color of this layout
                                              inline=True
                                          )
                                      ],
                                  ),
                                  dcc.Graph(
                                      id="delay_per_day"),
                              ], color=theme_color, inverse=True)
                              ], width=6)

        ]), color="#202022", inverse=True),
        html.H1("AIRPORT_MAP"),
        dbc.Card(children=[
            dbc.CardBody([
                dbc.FormGroup(
                    [
                        dbc.RadioItems(
                            options=[
                                {"label": "ORIGIN", "value": "origin"},
                                {"label": "DESTINATION", "value": "destination"}
                            ],
                            value="origin",
                            id="origin_or_destination",
                            inline=True,
                            labelCheckedStyle={"color": "#3b6978"}
                        )
                    ]
                ), dcc.Graph(
                    id="airport_map"
                ),
                # html.H1("top 20 cities"),
                # dcc.Graph(
                #     id = "analysis"
                # )
            ])], color="#202022", inverse=True),

    ])
])


# @app.callback(
#     Output("flight_map", "figure"),
#     inputs=[Input(airline, "n_clicks") for airline in airlines["IATA_CODE"]],
# )
# def update_map(*args):
#     trigger = callback_context.triggered[0]
#     airline = trigger["prop_id"].split(".")[0] if trigger["prop_id"].split(".")[0] else "UA"
#     paths = delay_flights[delay_flights["AIRLINE"] == airline]
#
#     fig = go.Figure()
#
#     for index, row in paths.iterrows():
#         fig.add_trace(go.Scattermapbox(
#             mode="markers+lines",
#             lat=[row["ORIGIN_LAT"], row["DESTINATION_LAT"]],
#             lon=[row["ORIGIN_LON"], row["DESTINATION_LON"]],
#             marker={'size': 3, 'symbol': ["airport", "airport"],
#                     },
#             line={'color': '#84a9ac', 'width': row["DELAY_RATE"]}
#         ))
#
#     fig.update_layout(
#         autosize=True,
#         mapbox=dict(
#             accesstoken=token,
#             style="dark",
#             bearing=0,
#             pitch=0,
#             zoom=3,
#             center=dict(
#                 lat=38,
#                 lon=-94
#             ),
#         ),
#         margin=go.layout.Margin(
#             l=0,  # left margin
#             r=0,  # right margin
#             b=0,  # bottom margin
#             t=0,  # top margin
#         ),
#         showlegend=False,
#     )
#     return fig
#
#
@app.callback(
    [Output(airline, "active") for airline in airlines["IATA_CODE"]],
    inputs=[Input(airline, "n_clicks") for airline in airlines["IATA_CODE"]],
)
def update_button_active(*args):
    trigger = callback_context.triggered[0]
    a = trigger["prop_id"].split(".")[0] if trigger["prop_id"].split(".")[0] else "UA"

    return [airline == a for airline in airlines["IATA_CODE"]]


@app.callback(
    Output("delay_per_day", "figure"),
    [Input(airline, "active") for airline in airlines["IATA_CODE"]],
    Input("arrival_or_departure", "value")
)
def update_delays(*args):
    delay_type = args[-1]
    # trigger = callback_context.triggered[0]
    # a = trigger["prop_id"].split(".")[0] if trigger["prop_id"].split(".")[0] else "HA"

    # click on which airline to choose
    a = "UA"
    for i in range(len(airlines["IATA_CODE"])):
        if args[i] == True:
            a = airlines["IATA_CODE"][i]
            break

    # plot the short delay boxplot of arrival
    fig = go.Figure()
    tick_interval = 1.1  # set the tick interval
    # process the arrival delay
    arrival_delay = arrival_delays[arrival_delays['AIRLINE'] == a]
    arrival_min = arrival_delay["ARRIVAL_DELAY_MIN"]
    arrival_max = arrival_delay["ARRIVAL_DELAY_MAX"]
    arrival_small_delay = arrival_delay["ARRIVAL_DELAY_WITHOUT_OUTLIER"]


    # plot the short delay boxplot
    for date, data in zip(list(np.arange(0.65, 16, tick_interval)), arrival_small_delay):
        hover_list = list(map(lambda x: (x - 15) * 0.8, ast.literal_eval(data)))
        hover_mean = np.mean(list(map(lambda x: x/0.8+15, hover_list)))
        fig.add_trace(go.Box(
            y=list(map(lambda x: (x - 15) * 0.8, ast.literal_eval(data))),
            x=[date] * len(ast.literal_eval(data)),
            boxpoints=False,
            boxmean=True,
            marker_color='#002d55' if delay_type == "arrival" else "gray",
            opacity=1 if delay_type == "arrival" else 0.3,
            showlegend=False,
            hoverinfo=[] if delay_type == "arrival" else 'skip',
        ))

    # plot the long delay line
    for i in np.arange(0, len(arrival_min)):
        trans_y0 = list(arrival_min)[i] * 1.2 - 5
        trans_y1 = list(arrival_max)[i] * 1.2 - 5
        if list(arrival_min)[i]:  # make sure not to plot the zero percentile

            # plot the upper line first
            fig.add_shape(type='line', x0=0.5 + i * tick_interval, x1=0.5 + i * tick_interval + 0.2,
                          y0=trans_y0, y1=trans_y0,
                          line=dict(color="#002d55" if delay_type == "arrival" else "rgba(102,102,102,0.2)"))

            # then plot the above line
            fig.add_shape(type='line', x0=0.5 + i * tick_interval, x1=0.5 + i * tick_interval + 0.2,
                          y0=trans_y1, y1=trans_y1,
                          line=dict(color="#002d55" if delay_type == "arrival" else "rgba(102,102,102,0.2)"))

            # finally plot the vertical line
            fig.add_shape(type='line', x0=0.7 + i * tick_interval, x1=0.7 + i * tick_interval,
                          y0=trans_y0, y1=trans_y1,
                          line=dict(color="#002d55" if delay_type == "arrival" else "rgba(102,102,102,0.2)"))

            # annotate the text of percentile
            fig.add_trace(go.Scatter(
                x=[0.2 + i * tick_interval, 0.2 + i * tick_interval],
                y=[trans_y0, trans_y1],

                text=[round(list(arrival_min)[i] / 100, 2),
                      round(list(arrival_max)[i] / 100, 2),
                      ],
                mode="text",
                showlegend=False,
                textfont=dict(color="#002d55" if delay_type == "arrival" else "rgba(102,102,102,0.2)"),
                hoverinfo='skip'

            ))

    # process the departure delay
    departure_delay = departure_delays[departure_delays['AIRLINE'] == a]
    departure_min = departure_delay["DEPARTURE_DELAY_MIN"]
    departure_max = departure_delay["DEPARTURE_DELAY_MAX"]
    departure_small_delay = departure_delay["DEPARTURE_DELAY_WITHOUT_OUTLIER"]

    # plot short delay of departure, the same as above
    for date, data in zip(list(np.arange(0.95, 16, tick_interval)), departure_small_delay):
        fig.add_trace(go.Box(
            y=list(map(lambda x: (x - 15) * 0.8, ast.literal_eval(data))),
            x=[date] * len(ast.literal_eval(data)),
            boxpoints=False,
            boxmean=True,
            marker_color='#002d55' if delay_type == "departure" else "gray",
            opacity=1 if delay_type == "departure" else 0.3,
            hoverinfo=[] if delay_type == "departure" else 'skip',
            showlegend=False
        ))

    # plot the long delay line of departure
    for i in np.arange(0, len(departure_min)):
        trans_y0_d = list(departure_min)[i]
        trans_y1_d = list(departure_max)[i]
        if list(departure_min)[i]:
            fig.add_shape(type='line', x0=0.8 + i * tick_interval, x1=0.8 + i * tick_interval + 0.2,
                          y0=trans_y0_d, y1=trans_y0_d,
                          line=dict(color="#002d55" if delay_type == "departure" else "rgba(102,102,102,0.2)"))

            fig.add_shape(type='line', x0=0.8 + i * tick_interval, x1=0.8 + i * tick_interval + 0.2,
                          y0=trans_y1_d, y1=trans_y1_d,
                          line=dict(color="#002d55" if delay_type == "departure" else "rgba(102,102,102,0.2)"))

            fig.add_shape(type='line', x0=0.8 + i * tick_interval, x1=0.8 + i * tick_interval,
                          y0=trans_y0_d, y1=trans_y1_d,
                          line=dict(color="#002d55" if delay_type == "departure" else "rgba(102,102,102,0.2)"))

            fig.add_trace(go.Scatter(
                x=[1.4 + i * tick_interval, 1.4 + i * tick_interval],
                y=[list(departure_min)[i], list(departure_max)[i]],
                text=[round(list(departure_min)[i] / 100, 2),
                      round(list(departure_max)[i] / 100, 2),
                      ],
                mode="text",
                showlegend=False,
                textfont=dict(color="#002d55" if delay_type == "departure" else "rgba(102,102,102,0.2)"),
                hoverinfo='skip'
            ))

    # add the interaction with plot
    fig.update_xaxes(fixedrange=True)  # disable brush on the plot
    fig.update_yaxes(fixedrange=True)
    fig.update_layout(
        xaxis=dict(
            title='date',
            zeroline=False,  # not include zero origin
            color='#002d55',
            range=(-0.5, 16.5),  # set the range of xaxis
            tickmode="array",
            tickvals=list(np.arange(0.8, 16, 1.1)),  # set the value of each tick
            ticktext=['Dec18', 'Dec19', 'Dec20', 'Dec21', 'Dec22', 'Dec23', 'Dec24',
                      'Dec25', 'Dec26', 'Dec27', 'Dec28', 'Dec29', 'Dec30', 'Dec31'],  # set the text of each tick
            showticklabels=True,
            ticklen=0,
            tickfont=dict(
                family="sans-serif",
                color="#002d55"
            ),
            rangeslider=dict(
                visible=False
            )  # disable the slider
        ),
        yaxis=dict(
            range=(-40, 125),
            showticklabels=False,
        ),
        font=dict(
            family="sans-serif",
        ),
        boxgroupgap=0.005,
        boxgap=0.385,  # set the width of boxplot
        plot_bgcolor='rgba(0,0,0,0)',
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin
            autoexpand=True
        ),
        paper_bgcolor='rgba(0,0,0,0)',

    )
    return fig


# @app.callback(
#     Output("airport_map", "figure"),
#     Input("origin_or_destination", "value")
# )
# def update_airport_map(v):
#     fig = go.Figure()
#     if v == "origin":
#         fig = px.scatter_mapbox(origin, lat="LAT", lon="LON", color="DELAY_RATE", size="SUM", mapbox_style="dark",
#                                 color_continuous_scale=px.colors.cyclical.IceFire, zoom=3,
#                                 hover_data=["NAME", "CITY"]
#                                 )
#         # fig = go.Figure()
#         # fig.add_trace(go.Scattermapbox(
#         #     lat=origin["LAT"],
#         #     lon=origin["LON"],
#         #     marker=dict(
#         #         color=origin["DELAY_RATE"],
#         #         colorscale="icefire",
#         #         # size=origin["SUM"],
#         #         showscale=True
#         #     ),
#         # ))
#         fig.update_layout(
#             # mapbox=dict(
#             #     accesstoken=token,
#             #     style="dark",
#             #     bearing=0,
#             #     pitch=0,
#             #     zoom =3,
#             #     center=dict(
#             #         lat=38,
#             #         lon=-94
#             #     ),
#             # ),
#             template="plotly_dark",
#             margin=go.layout.Margin(
#                 l=0,  # left margin
#                 r=0,  # right margin
#                 b=0,  # bottom margin
#                 t=0,  # top margin
#                 autoexpand=True
#             ),
#             paper_bgcolor='rgb(10,10,10)'
#         )
#     else:
#         fig = px.scatter_mapbox(destination, lat="LAT", lon="LON", color="DELAY_RATE", size="SUM", mapbox_style="dark",
#                                 color_continuous_scale=px.colors.cyclical.IceFire, zoom=3, hover_data=["NAME", "CITY"])
#         # fig = go.Figure()
#         # fig.add_trace(go.Scattermapbox(
#         #     lat=destination["LAT"],
#         #     lon=destination["LON"],
#         #     marker=dict(
#         #         color=destination["DELAY_RATE"],
#         #         colorscale="icefire",
#         #         # size=destination["SUM"],
#         #         showscale=True
#         #     ),
#         # ))
#         fig.update_layout(
#             margin=go.layout.Margin(
#                 l=0,  # left margin
#                 r=0,  # right margin
#                 b=0,  # bottom margin
#                 t=0,  # top margin
#                 autoexpand=True
#             ),
#             paper_bgcolor='rgb(10,10,10)'
#         )
#     return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1')

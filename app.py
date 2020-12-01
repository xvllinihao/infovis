import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash import callback_context
from dash.dependencies import Output, Input
import plotly.express as px
from plotly.subplots import make_subplots

external_stylesheets = [dbc.themes.DARKLY]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options


airlines = pd.read_csv("data/airlines.csv")
airports = pd.read_csv("data/airports.csv")
delay_flights = pd.read_json("data/delay_flights.json")
arrival_delays = pd.read_json("data/arrival_delay_per_day.json")
departure_delays = pd.read_json("data/departure_delay_per_day.json")
origin = pd.read_json("data/origin.json")
destination = pd.read_json("data/destination.json")
flights_per_day = pd.read_json("data/flights_per_day.json")

px.set_mapbox_access_token(open("data/.mapbox_token").read())
token = open("data/.mapbox_token").read()

city_dic = {}
airport_name_dic = {}
for idx, row in airports.iterrows():
    city_dic[row["IATA_CODE"]] = row["CITY"]
    airport_name_dic[row["IATA_CODE"]] = row["AIRPORT"]

origin_city_list = []
origin_name_list = []
for idx,row in origin.iterrows():
    origin_city_list.append(city_dic[row["ORIGIN_AIRPORT"]])
    origin_name_list.append(airport_name_dic[row["ORIGIN_AIRPORT"]])
origin["CITY"] =origin_city_list
origin["NAME"] = origin_name_list

destination_city_list = []
destination_name_list = []

for idx,row in destination.iterrows():
    destination_city_list.append(city_dic[row["DESTINATION_AIRPORT"]])
    destination_name_list.append(airport_name_dic[row["DESTINATION_AIRPORT"]])
destination["CITY"] = destination_city_list
destination["NAME"] = destination_name_list


def get_flights_figure():
    flights_figure = go.Figure()
    flights_figure.add_trace(go.Scatter(
        x=flights_per_day["DATE"],
        y=flights_per_day["SUM"],
        mode="lines+markers"
    ))
    flights_figure.update_layout(
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin
            autoexpand=True
        ),
        paper_bgcolor='rgb(10,10,10)',
        plot_bgcolor='rgb(10,10,10)'
    )
    return flights_figure


app.layout = html.Div(children=[
    dbc.Container(children=[
        dbc.Card(children=
        dbc.Row([
            dbc.Col(children=[
                dbc.Badge("AIRLINE", color="info", className="mr-1"),
                dbc.ButtonGroup(
                    [dbc.Button(airline, id=airline, outline=False, color="success", className="mr-1") for airline in
                     airlines["IATA_CODE"]],
                    size="md",
                    id="airline_input",
                    vertical=True
                )], width=1),
            dbc.Col(children=[
                html.H1("FLIGHT_MAP"),
                dcc.Graph(
                    id="flight_map",
                ),
                html.H1("DELAY_PER_DAY"),
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
                                labelCheckedStyle={"color": "darkred"},
                                inline=True
                            )
                        ],
                    ),
                    dcc.Graph(
                        id="delay_per_day"
                    ), ], color="secondary", inverse=True)
            ], width=11)
        ]), color="secondary", inverse=True),
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
                        labelCheckedStyle={"color": "darkred"}
                    )
                ]
            ), dcc.Graph(
                id="airport_map"
            ),
            html.H1("top 20 cities"),
            dcc.Graph(
                id = "analysis"
            )
            ])], color="secondary", inverse=True),

        html.H1("FLIGHTS_PER_DAY"),
        dbc.Card(
        dcc.Graph(
            id="flights_graph",
            figure=get_flights_figure()
        ),color="secondary",inverse=True,outline=True)
    ])
])


@app.callback(
    Output("flight_map", "figure"),
    inputs=[Input(airline, "n_clicks") for airline in airlines["IATA_CODE"]],
)
def update_map(*args):
    trigger = callback_context.triggered[0]
    airline = trigger["prop_id"].split(".")[0] if trigger["prop_id"].split(".")[0] else "UA"
    paths = delay_flights[delay_flights["AIRLINE"] == airline]

    fig = go.Figure()

    for index, row in paths.iterrows():
        fig.add_trace(go.Scattermapbox(
            mode="markers+lines",
            lat=[row["ORIGIN_LAT"], row["DESTINATION_LAT"]],
            lon=[row["ORIGIN_LON"], row["DESTINATION_LON"]],
            marker={'size': 3, 'symbol': ["airport", "airport"],
                    },
            line={'color': 'darkorange', 'width': row["DELAY_RATE"]}
        ))

    fig.update_layout(
        autosize=True,
        mapbox=dict(
            accesstoken=token,
            style="dark",
            bearing=0,
            pitch=0,
            zoom=3,
            center=dict(
                lat=38,
                lon=-94
            ),
        ),
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin
        ),
        showlegend=False,
    )
    return fig


@app.callback(
    [Output(airline, "active") for airline in airlines["IATA_CODE"]],
    inputs=[Input(airline, "n_clicks") for airline in airlines["IATA_CODE"]],
)
def update_button_active(*args):
    trigger = callback_context.triggered[0]
    a = trigger["prop_id"].split(".")[0] if trigger["prop_id"].split(".")[0] else "HA"

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
    a = "HA"
    for i in range(len(airlines["IATA_CODE"])):
        if args[i] == True:
            a = airlines["IATA_CODE"][i]
            break

    arrival_delay = arrival_delays[arrival_delays['AIRLINE'] == a]
    departure_delay = departure_delays[departure_delays['AIRLINE'] == a]
    arrival_dates = arrival_delay["DATE"]
    arrival_datas = arrival_delay["ARRIVAL_DELAY"]
    fig = go.Figure()
    for date, data in zip(arrival_dates, arrival_datas):
        fig.add_trace(go.Box(
            y=data,
            x=[date] * len(data),
            jitter=0.3,
            marker_color='yellow' if delay_type == "arrival" else "gray",
            opacity=1 if delay_type == "arrival" else 0.8,
            hoverinfo=[] if delay_type == "arrival" else "skip",
            showlegend=False
        ))

    departure_dates = departure_delay["DATE"]
    departure_datas = departure_delay["DEPARTURE_DELAY"]

    for date, data in zip(departure_dates, departure_datas):
        fig.add_trace(go.Box(
            y=data,
            x=[date] * len(data),
            jitter=0.3,
            marker_color='gray' if delay_type == "arrival" else "yellow",
            opacity=0.8 if delay_type == "arrival" else 1,
            hoverinfo="skip" if delay_type == "arrival" else [],
            showlegend=False
        ))

    fig.update_layout(
        xaxis=dict(title='ARRIVAL_DELAY', zeroline=False, color='rgb(10,10,10)',
                   tickfont=dict(
                       family="Times New Roman",
                       color="yellow"
                   ),
                   rangeslider=dict(
                       visible=True
                   ),
                   type="date"),
        yaxis=dict(range=[0, 100], tickfont=dict(
            family="Times New Roman",
            color="yellow"
        ), ),
        boxmode='overlay',
        boxgap=0,
        plot_bgcolor='rgb(10,10,10)',
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin
            autoexpand=True
        ),
        paper_bgcolor='rgb(10,10,10)'
    )
    return fig


@app.callback(
    Output("airport_map", "figure"),
    Input("origin_or_destination", "value")
)
def update_airport_map(v):
    fig = go.Figure()
    if v == "origin":
        fig =px.scatter_mapbox(origin, lat="LAT", lon="LON", color="DELAY_RATE", size="SUM", mapbox_style="dark",
                                color_continuous_scale=px.colors.cyclical.IceFire, zoom=3,
                               hover_data=["NAME","CITY"]
                               )
        # fig = go.Figure()
        # fig.add_trace(go.Scattermapbox(
        #     lat=origin["LAT"],
        #     lon=origin["LON"],
        #     marker=dict(
        #         color=origin["DELAY_RATE"],
        #         colorscale="icefire",
        #         # size=origin["SUM"],
        #         showscale=True
        #     ),
        # ))
        fig.update_layout(
            # mapbox=dict(
            #     accesstoken=token,
            #     style="dark",
            #     bearing=0,
            #     pitch=0,
            #     zoom =3,
            #     center=dict(
            #         lat=38,
            #         lon=-94
            #     ),
            # ),
            template="plotly_dark",
            margin=go.layout.Margin(
                l=0,  # left margin
                r=0,  # right margin
                b=0,  # bottom margin
                t=0,  # top margin
                autoexpand=True
            ),
            paper_bgcolor='rgb(10,10,10)'
        )
    else:
        fig=px.scatter_mapbox(destination, lat="LAT", lon="LON", color="DELAY_RATE", size="SUM", mapbox_style="dark",
                                color_continuous_scale=px.colors.cyclical.IceFire, zoom=3, hover_data=["NAME","CITY"])
        # fig = go.Figure()
        # fig.add_trace(go.Scattermapbox(
        #     lat=destination["LAT"],
        #     lon=destination["LON"],
        #     marker=dict(
        #         color=destination["DELAY_RATE"],
        #         colorscale="icefire",
        #         # size=destination["SUM"],
        #         showscale=True
        #     ),
        # ))
        fig.update_layout(
            margin=go.layout.Margin(
                l=0,  # left margin
                r=0,  # right margin
                b=0,  # bottom margin
                t=0,  # top margin
                autoexpand=True
            ),
            paper_bgcolor='rgb(10,10,10)'
        )
    return fig

@app.callback(
    Output("analysis", "figure"),
    Input("origin_or_destination", "value")
)
def update_analysis(v):
    data = origin if v == "origin" else destination
    data = data.nlargest(20,"SUM")

    #fig = px.pie(data, values="SUM",labels="ORIGIN_AIRPORT" if v=="origin" else "DESTINATION_AIRPORT",color_discrete_sequence=px.colors.sequential.Viridis,hole=0.5)
    fig = px.bar(data,x="CITY",y="SUM",color="CITY",
                 color_continuous_scale=px.colors.cyclical.IceFire)


    fig.update_layout(
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin
            autoexpand=True
        ),
        paper_bgcolor='rgb(10,10,10)',
        plot_bgcolor = 'rgb(10,10,10)'
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from pandas_datareader import data

from datetime import date

def update_data():
    # !! reset_index because otherwise plotly doesn't recognize the index as a x input in go.Figure
    df = data.DataReader('USDJPY%3DX', data_source='yahoo', start=start, end=end).reset_index()
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    return fig

app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

start = pd.to_datetime('2022-01-01')
end = pd.to_datetime(date.today())

app.layout = dbc.Container(
    [
        dbc.Row(
            [dbc.Col([html.H1(
                    "Daily Price",
                        style={"textAlign": "center"},
                    ),
                    dcc.Graph(id="price-chart", figure={})],
                    width=12,lg=6),
            dbc.Col([html.H1(
                    "Daily 15-minute standard deviation",
                        style={"textAlign": "center"},
                    ),
                    dcc.Graph(id="volatility-chart", figure={})],
                    width=12,lg=6)
            ]
        ),
        dbc.Row(
            dbc.Col(dcc.Dropdown(
                        id="dropdown",
                        options=["AAPL", "TSLA", "MSFT"],
                        value=["TSLA"],
                        style={"color": "green"}
                    ),
                    className="three columns"),
        ),
    dcc.Store(id="storage", storage_type="memory", data={}),
    dcc.Interval(id="timer", interval=1000 * 60, n_intervals=0),
    ]
)

# Stopped here @ 20:51 figure out why I get an error on the timer component
@app.callback(Output(component_id = "storage", component_property = "data"),
                Input(component_id = "timer", component_property = "n_intervals"))    #### Note that the
def store_data(n_time):
    df = update_data()                                                                           # prop has to coincide with the particular property of that same component!
    return df.to_dict("records")

@app.callback(Output(component_id = "price-chart", component_property = "figure"),
                Input(component_id = "storage", component_property = "data"))
def display_data(stored_dataframe):
    return pd.DataFrame.from_records(stored_dataframe)

@app.callback(Output(component_id = "volatility-chart", component_property = "figure"),
                Input(component_id = "storage", component_property = "data"))    #### Note that the
def modify_data(stored_dataframe):
    df = pd.DataFrame.from_records(stored_dataframe)
    res = df.resample('10d').sd()                                                                          # prop has to coincide with the particular property of that same component!
    return res

if __name__ == "__main__":
    app.run_server(debug=True)

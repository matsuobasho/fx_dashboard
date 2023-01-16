from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import pandas as pd
from pandas_datareader import data
import yfinance as yf
yf.pdr_override()

from datetime import date

# Data prep *******************************************

start = pd.to_datetime('2022-01-01')
end = pd.to_datetime(date.today())

df = data.DataReader('USDJPY%3DX', data_source='yahoo', start=start, end=end)
df_mod = df.copy()

df_mod['1-day'] = (df_mod.High - df_mod.Low) * 100
df_mod['2-day'] = df_mod['1-day'].rolling(2).mean()
df_mod['5-day'] = df_mod['1-day'].rolling(5).mean()
df_mod['10-day'] = df_mod['1-day'].rolling(10).mean()

nikkei = data.DataReader('^N225', start='2022-01-01', data_source='yahoo')
sp = data.DataReader('^GSPC', start='2022-01-01', data_source='yahoo')

# Figures

price_fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])]).update_layout(xaxis_rangeslider_visible=False)

def create_double_ax_plot(df1, df2, df1_label, df2_label):
    tmp = make_subplots(specs=[[{"secondary_y": True}]])
    tmp.add_trace(
            go.Scatter(x=df1.index, y=df1.Close, name=df1_label),
            secondary_y=False,
            )
    tmp.add_trace(
            go.Scatter(x=df2.index, y=df2.Close, name=df2_label),
            secondary_y=True,
    )

    tmp.update_xaxes(title_text="Date")
    tmp.update_yaxes(title_text=df1_label, secondary_y=False)
    tmp.update_yaxes(title_text=df2_label, secondary_y=True)

    return tmp

nik_fig = create_double_ax_plot(nikkei, df, 'Nikkei', 'USD/JPY rate')
sp_fig = create_double_ax_plot(sp, df, 'S&P', 'USD/JPY rate')

# App Layout *******************************************

app = Dash(__name__, external_stylesheets=[dbc.themes.LITERA])

# def update_data():
#     # !! reset_index because otherwise plotly doesn't recognize the index as a x input in go.Figure
#     df = data.DataReader('USDJPY%3DX', data_source='yahoo', start=start, end=end).reset_index()
#     return df

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H2(
                    "USD/JPY Dashboard",
                    className="text-center bg-primary text-white p-2",
                ),
            )
        ),
        dbc.Row(
            [
                dbc.Col([html.H3(
                        "Daily Price",
                            style={"textAlign": "center"},
                        ),
                        dcc.Graph(id="price-chart", figure=price_fig)],
                        width=12,lg=5),
                dbc.Col([html.H3(
                        "Daily Range SMA",
                            style={"textAlign": "center"},
                        ),
                        dcc.Graph(id="vol-chart", figure={})],
                        width=12,lg=5),
                dbc.Col([dbc.RadioItems(
                            id='sma-radio',
                            options=[{"label": i, "value": i} for i in ['1-day', '2-day', '5-day', '10-day']],
                            value='10-day',
                            #input_class_name="mt-5",
                            )
                        ]
                        ,
                        width = 12, lg=2)
            ]
        ),
        dbc.Row(
            dbc.Col(html.H2(
                    "Correlations"),
                    className="text-center"),
            ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="nikkei", figure=nik_fig),
                    width=12, lg=6
                    ),
                dbc.Col(
                    dcc.Graph(id="sp", figure=sp_fig),
                    width=12, lg=6
                    ),
            ]
            ),
    #dcc.Store(id="storage", storage_type="session", data={}),
    #dcc.Interval(id="timer", interval=1000 * 60, n_intervals=0),
    ]
)

# Callbacks ***************************************************************

# @app.callback(Output(component_id = "storage", component_property = "data"),
#                 Input(component_id = "timer", component_property = "n_intervals"))
# def store_data(n_time):
#     df = update_data()
#     return df.to_dict("records")

@app.callback(Output(component_id = "vol-chart", component_property = "figure"),
                Input(component_id = "sma-radio", component_property = "value"))
def display_data(time_frame):
    vol_fig = px.line(df_mod[time_frame]).update_layout(yaxis_title="Pips").update_traces(showlegend=False)

    return vol_fig

if __name__ == "__main__":
    app.run_server(debug=True)

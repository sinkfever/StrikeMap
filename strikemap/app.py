from dotenv import load_dotenv
from schwab.auth import easy_client

import dash
from dash import Dash, dcc, html, Input, Output, State, callback

import plotly
# import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import datetime
import numpy as np
import pandas as pd
import os
import time

load_dotenv()

client = easy_client(
        api_key = os.getenv('SCHWAB_API_KEY'),
        app_secret = os.getenv('SCHWAB_API_SECRET'),
        callback_url = 'https://127.0.0.1:8182',
        token_path = os.getenv('SCHWAB_TOKEN_PATH')
)

TICKER = 'QQQ'
STRIKE_COUNT = 50

def pull_option_chain(client, ticker, strike_count = STRIKE_COUNT, from_date = datetime.date.today(), to_date = datetime.date.today()):
    return client.get_option_chain(
            contract_type = client.Options.ContractType('ALL'),
            symbol = ticker,
            strike_count = strike_count,
            from_date = from_date,
            to_date = to_date
    ).json()


def get_option_data(data, ticker, side, single_data=False, strike_target=0):
    chain = pull_option_chain(client, ticker)
    data_points = dict()
    if side == 'c':
        for date in chain['callExpDateMap']:
            for strike in chain['callExpDateMap'][date]:
                if strike_target == 0:
                    if single_data:
                       return float(chain['callExpDateMap'][date][strike][0][data])
                    data_points[float(strike)] = chain['callExpDateMap'][date][strike][0][data]
                else:
                    if float(strike) == strike_target:
                        if single_data:
                            return float(chain['callExpDateMap'][date][strike][0][data])
                        data_points[float(strike)] = chain['callExpDateMap'][date][strike][0][data]
    elif side == 'p':
        for date in chain['putExpDateMap']:
            for strike in chain['putExpDateMap'][date]:
                if strike_target == 0:
                    if single_data:
                       return float(chain['putExpDateMap'][date][strike][0][data])
                    data_points[float(strike)] = chain['putExpDateMap'][date][strike][0][data]
                else:
                    if float(strike) == strike_target:
                        if single_data:
                            return float(chain['putExpDateMap'][date][strike][0][data])
                        data_points[float(strike)] = chain['putExpDateMap'][date][strike][0][data]

    return data_points


# Options Volume Flow
# To scale up to multiple strikes instead of one, a dictionary should be returned
# Set a dictionary to be the previous volume set, if none exists yet, set the current as previous
# Get the new set of volume data in the next second, then use NumPy operations to subtract the difference
#   between the new and old volume data 
# DO NOT make the strike axis dynamic, as it can shift between each data set.


app = dash.Dash(__name__)
app.layout = html.Div(
        [
            dcc.Graph(id = 'graph'),
            dcc.Interval(
                id = 'interval-component',
                interval = 1000,
                n_intervals = 0
            ),
            dcc.Store(id='prev-volume', storage_type='memory')
        ]
)

# Volume Hypothesis 2
# If option transactions are closer to a normal curve rather than random buying points:
#   (An approximate normal curve would have the peak of transactions at spot, and decrease accordingly
#       on each side)
# Then it could signify heavier moves, we also need sizing of transactions to be high.
#   TODO: Find a way to determine usual transaction sizing for the day.
# 
# For now, strictly for the hypothesis:
# Assume activity on the call side will result in bullish action
#   and put side will result in bearish action on price. This is 
#   very likely not true at all due to calls and puts having both bullish
#   and bearish strategies, but it's worth checking for hidden correlations
#   

def compute_volume_flow(cur_vol, prev_vol, elapsed_time):
    cur_vol_series = pd.Series(cur_vol)
    prev_vol_series = pd.Series(prev_vol)
    cur_vol_series.index = cur_vol_series.index.astype(float)
    prev_vol_series.index = prev_vol_series.index.astype(float)
    return ((cur_vol_series - prev_vol_series).dropna() / elapsed_time).sort_index()


@app.callback(
        Output('graph', 'figure'),
        Output('prev-volume', 'data'),
        Input('interval-component', "n_intervals"),
        State('prev-volume', 'data')
)

def update_graph(n, prev_volume):
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True)

    current_volume = {
        'c': get_option_data(data='totalVolume', ticker=TICKER, side='c'),
        'p': get_option_data(data='totalVolume', ticker=TICKER, side='p'),
    }

    if not prev_volume or 'c' not in prev_volume or 'p' not in prev_volume:
        return fig, current_volume

    rate_of_change = compute_volume_flow(current_volume['c'], prev_volume['c'], 1)
    fig.add_trace(go.Bar(x=rate_of_change.index, y=rate_of_change.values), row=1, col=1)

    rate_of_change = compute_volume_flow(current_volume['p'], prev_volume['p'], 1)
    fig.add_trace(go.Bar(x=rate_of_change.index, y=rate_of_change.values), row=1, col=2)

    return fig, current_volume

if __name__ == '__main__':
    app.run(debug=True)

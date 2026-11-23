from dotenv import load_dotenv
from schwab.auth import easy_client

import dash
from dash import Dash, dcc, html, Input, Output, State, callback
import plotly
import plotly.express as px

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

CALL = client.Options.ContractType('CALL')
PUT = client.Options.ContractType('PUT')

def pull_option_chain(client, ticker, side = CALL, strike_count = 40, from_date = datetime.date.today(), to_date = datetime.date.today()):
    return client.get_option_chain(
            contract_type = side,
            symbol = ticker,
            strike_count = strike_count,
            from_date = from_date,
            to_date = to_date
    ).json()

test_pull = pull_option_chain(client, 'SPY')
# print(test_pull)

def get_option_data(data, side, single_data=False, strike_target=0):
    chain = pull_option_chain(client, 'SPY')
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
                interval = 1500,
                n_intervals = 0
            ),
            dcc.Store(id='prev-volume', storage_type='local')
        ]
)

@app.callback(
        Output('graph', 'figure'),
        Output('prev-volume', 'data'),
        Input('interval-component', "n_intervals"),
        State('prev-volume', 'data')
)

def update_graph(n, prev_volume):
    data = dict()
    if prev_volume is None:
        prev_volume = get_option_data(data='totalVolume', side='c')
    else:
        current_volume = get_option_data(data='totalVolume', side='c')
        rate_of_change = np.subtract(list(current_volume.values()), list(prev_volume.values())).tolist()
        prev_volume = current_volume
        print(rate_of_change)
        print('Average Volume ROC:', np.average(rate_of_change), 'contracts per second')
        data = dict(zip(current_volume.keys(), rate_of_change))
    df = pd.DataFrame({
        "strike": list(data.keys()),
        "value": list(data.values()),
    })
    return px.bar(df, x="strike", y="value", range_y=[0, 500]), prev_volume


if __name__ == '__main__':
    app.run(debug=True)

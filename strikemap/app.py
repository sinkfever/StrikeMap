from dotenv import load_dotenv
from schwab.auth import easy_client

import datetime
import os

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

def get_option_prop(chain, prop, side):
    data_points = dict()
    if side == 'c':
        for date in chain['callExpDateMap']:
            for strike in chain['callExpDateMap'][date]:
                data_points[float(strike)] = chain['callExpDateMap'][date][strike][0][prop]

    return data_points

data = get_option_prop(test_pull, 'totalVolume', 'c')
print(data)


# Options Volume Flow
# Purpose: 
#   This idea attempts to show where option activity is currently active in real time, 
#   by taking the nth second's volume of a certain strike, then subtracting the nth second's volume from 
#   (n+1)th second's volume, to get the change of volume from the previous second to the current second 
# Example:
#   12:01:00 PM, SPY Volume at 750 = 85000
#   12:01:01 PM, SPY Volume at 750 = 86000
#   Options Volume RoC = (86000 - 85000) / (1 - 0) = 1000
# Implementation:
#   Gather data to figure out the range of "normal" RoC variance, then define anything outside of the variance
#       to be unusual activity. Volume RoC can help us figure out where trading activity is currently located. 
#       Consider this tool as a location tool.
# Hypothesis:
#   Sudden spike in volume flow at a strike that's on OTM on either tail can signify a potential move towards
#       that direction.
# Verdict: To be tested

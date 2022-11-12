import os
import pandas as pd
from binance import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
client = Client(API_KEY, API_SECRET)

# check that the connection is working
# print(client.get_account())

# getting 1m interval price data
# can also establish datastream via web socket

# pd.Datadf(client.get_historical_klines("BTCUSDT", "1m", "30m ago UTC"))

# provide symbol, time interval and lookbackperiod
# data cleanup
def getminutedata(symbol, interval, lookback):
    df = pd.DataFrame(
        client.get_historical_klines(symbol, interval, lookback + " min ago UTC")
    )
    # all the rows and up to column num 6 (volume inclusive)
    df = df.iloc[:, :6]
    df.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
    # set index to time (unix time)
    df = df.set_index("Time")
    df.index = pd.to_datetime(df.index, unit="ms")
    df = df.astype(float)
    print(df.index)

    return df


# buy if asset fell by more than 0.5% within last 30 mins
# sell if asset rises by more than 0.35% or falls further by 0.15%


def basicstrategy(symbol, qty, tf, lookback, entry=False):
    df = getminutedata(symbol, tf, lookback)

    # rate of change of the Open price as a cumulitive product
    # simply put percent change from 30 mins ago up until now
    cumulret = (df.Open.pct_change() + 1).cumprod() - 1

    # if not in a trade
    if not entry:
        # buying condition
        if cumulret[-1] < -0.005:
            order = client.create_order(
                symbol=symbol, side="BUY", type="MARKET", quantity=qty
            )
            print(order)
            entry = True
        else:
            print("No Execution")

    # must reevaluate every minute to see how the asset has performed
    if entry:
        while True:
            df = getminutedata(symbol, tf, lookback)

            # timestamps after we have bought the asset
            sincebuy = df.loc[
                df.index > pd.to_datetime(order["transactTime"], unit="ms")
            ]
            if len(sincebuy) > 0:
                sincebuyret = (sincebuy.Open.pct_change() + 1).cumprod() - 1
                if sincebuyret[-1] > 0.0035 or sincebuyret[-1] < -0.0015:
                    order = client.create_order(
                        symbol=symbol, side="SELL", type="MARKET", quantity=qty
                    )
                    print(order)
                    break


def main():
    # basicstrategy("BTCUSDT", "0.001", "1m", "30")


if __name__ == "__main__":
    main()

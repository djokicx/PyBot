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

# pd.DataFrame(client.get_historical_klines("BTCUSDT", "1m", "30m ago UTC"))

# provide symbol, time interval and lookbackperiod
def getminutedata(symbol, interval, lookback):
    frame = pd.DataFrame(
        client.get_historical_klines(symbol, interval, lookback + " min ago UTC")
    )
    # all the rows and up to column num 6 (volume inclusive)
    frame = frame.iloc[:, :6]
    frame.columns = ["Time", "Open", "High", "Low", "Close", "Volume"]
    # set index to time (unix time)
    frame = frame.set_index("Time")
    frame.index = pd.to_datetime(frame.index, unit="ms")
    frame = frame.astype(float)
    print(frame)

    return frame


def main():
    getminutedata("BTCUSDT", "1m", "30")


if __name__ == "__main__":
    main()

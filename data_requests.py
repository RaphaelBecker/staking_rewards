import pathlib
import pandas as pd
import datetime
# DB Management
import requests
import sqlalchemy as sqlalchemy
import streamlit as st

db_name = 'HLOCV.db'
root_dir0 = pathlib.Path(__file__).resolve().parents[0]
db_path = 'sqlite:///' + str(pathlib.Path.joinpath(root_dir0, db_name))

engine = sqlalchemy.create_engine(db_path, echo=True, connect_args={"check_same_thread": False, 'timeout': 5})
conn = engine.connect()


def download_ticker_df(ticker, start, interval=1440):
    """
    Example requ: requests.get('https://api.kraken.com/0/public/OHLC?pair=XBTUSD')
    :param interval: timeframe in minutes (1d: 1440)
    :param ticker: str
    :param start: linuxtmps
    :return: pd.Dataframe
    """
    url = 'https://api.kraken.com/0/public/OHLC'
    params = {'pair': ticker, 'interval': interval, 'since': start}
    res = requests.get(url, params=params)
    data = res.json()
    print(data)
    if ticker == "XBTUSD":
        df = pd.DataFrame(data['result']["XXBTZUSD"])
    if ticker == "XBTEUR":
        df = pd.DataFrame(data['result']["XXBTZEUR"])
    else:
        df = pd.DataFrame(data['result'][ticker])
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']

    # Convert the columns to float
    df = df.apply(pd.to_numeric, errors='coerce')

    df['ticker'] = ticker
    return df


def add_ohlc(ticker, start):
    df = download_ticker_df(ticker, start)
    df.to_sql(ticker, engine, if_exists='replace', index=False)


def get_ohlc_from_db(ticker):
    sqlite_query_string = sqlalchemy.sql.text(f"SELECT * FROM {ticker}")
    df = pd.read_sql(sqlite_query_string, con=conn)
    return df


def get_ticker_from_db(ticker, timestamp):
    """
    :param ticker: str (SOLEUR)
    :param timestamp: linux timestamp
    :return:
    return df like:
        timestamp   open  high   low  close   vwap        volume  count  ticker
    0   1672012800  10.68  10.8  10.4  10.63  10.56  36129.483519   1115  SOLEUR
    """
    sqlite_query_string = sqlalchemy.sql.text(f"SELECT * FROM {ticker} WHERE timestamp = '{timestamp}'")
    df = pd.read_sql(sqlite_query_string, con=conn)
    if df.empty:
        st.error(f"ticker: {ticker} or/and timestamp: {timestamp} not in database")
    return df


def add_list_of_ohlc(ticker_list, start):
    for ticker in ticker_list:
        add_ohlc(ticker, start)


def get_list_of_ohlc_from_db(ticker_list):
    df_list = []
    for ticker in ticker_list:
        df_list.append(get_ohlc_from_db(ticker))
    return df_list


def close_db_connection(self):
    self.conn.close()

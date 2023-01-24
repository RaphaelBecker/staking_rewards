import sqlite3
import pandas as pd
import requests


def create_database():
    conn = sqlite3.connect('kraken.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kraken
                 (timestamp INTEGER, open REAL, high REAL, low REAL, close REAL, vwap REAL, volume REAL, count REAL, ticker TEXT)''')
    conn.commit()
    conn.close()


def get_data(ticker, start):
    """
    Example requ: requests.get('https://api.kraken.com/0/public/OHLC?pair=XBTUSD')
    :param ticker: str
    :param start: linuxtmps
    :return: pd.Dataframe
    """
    url = 'https://api.kraken.com/0/public/OHLC'
    params = {'pair': ticker, 'interval': 60, 'since': start}
    res = requests.get(url, params=params)
    data = res.json()
    print(data)
    if ticker == "XBTUSD":
        df = pd.DataFrame(data['result']["XXBTZUSD"])
    else:
        df = pd.DataFrame(data['result'][ticker])
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']

    # Convert the columns to float
    df = df.apply(pd.to_numeric, errors='coerce')

    df['ticker'] = ticker
    return df


def save_to_db(df):
    conn = sqlite3.connect('kraken.db')
    df.to_sql('kraken', conn, if_exists='append', index=False)
    conn.close()


def get_data_from_db(ticker, start, end):
    conn = sqlite3.connect('kraken.db')
    df = pd.read_sql_query(
        "SELECT * FROM kraken WHERE ticker='{}' AND timestamp >= {} AND timestamp <= {}".format(ticker, start, end),
        conn)
    conn.close()
    return df

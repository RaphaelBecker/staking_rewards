import sqlite3
import pandas as pd
import requests


def create_database():
    conn = sqlite3.connect('kraken.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kraken
                 (timestamp INTEGER, ticker TEXT, open REAL, high REAL, low REAL, close REAL)''')
    conn.commit()
    conn.close()


def get_data(ticker, start, end):
    url = 'https://api.kraken.com/0/public/OHLC'
    params = {'pair': ticker, 'interval': 1, 'since': start}
    res = requests.get(url, params=params)
    data = res.json()
    df = pd.DataFrame(data['result'][ticker],
                      columns=['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
    df['ticker'] = ticker
    df = df[df['timestamp'] <= end]
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

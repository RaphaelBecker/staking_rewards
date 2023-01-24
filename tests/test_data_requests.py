import sqlite3
import unittest
import data_requests
import pandas as pd


class TestKrakenModule(unittest.TestCase):

    def test_create_database(self):
        data_requests.create_database()
        conn = sqlite3.connect('kraken.db')
        c = conn.cursor()
        c.execute("SELECT name from sqlite_master WHERE type='table' AND name='kraken'")
        result = c.fetchone()
        conn.close()
        self.assertEqual(result[0], 'kraken')

    def test_get_data(self):
        ticker = 'XBTUSD'
        start = 1609459200
        df = data_requests.get_data(ticker, start)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('timestamp', df.columns)
        self.assertIn('ticker', df.columns)
        self.assertEqual(df['ticker'][0], ticker)
        print(df.dtypes)

    def test_save_to_db(self):
        ticker = 'XBTUSD'
        start = 1609459200
        df = data_requests.get_data(ticker, start)
        data_requests.save_to_db(df)
        conn = sqlite3.connect('kraken.db')
        df_from_db = pd.read_sql_query("SELECT * FROM kraken", conn)
        conn.close()
        pd.testing.assert_frame_equal(df, df_from_db)

    def test_get_data_from_db(self):
        ticker = 'BTCUSD'
        start = 1609459200
        end = 1609541200
        df = data_requests.get_data_from_db(ticker, start, end)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('timestamp', df.columns)
        self.assertIn('ticker', df.columns)
        self.assertEqual(df['ticker'][0], ticker)
        self.assertTrue((df['timestamp'] >= start).all() and (df['timestamp'] <= end).all())


if __name__ == '__main__':
    unittest.main()

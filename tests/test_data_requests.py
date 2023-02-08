import sqlite3
import unittest
import data_requests
import pandas as pd


class TestKrakenModule(unittest.TestCase):

    def test_get_data(self):
        ticker = 'XBTUSD'
        start = 1609459200
        df = data_requests.download_ticker_df(ticker, start)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('timestamp', df.columns)
        self.assertIn('ticker', df.columns)
        self.assertEqual(df['ticker'][0], ticker)
        print(df.dtypes)

    def test_add_hlocv_table(self):
        ticker = 'XBTEUR'
        start = 1609459200
        data_requests.add_ohlc(ticker, start)

    def test_get_hlocv_db(self):
        ticker = 'XBTUSD'
        print(data_requests.get_ohlc_from_db(ticker))

    def test_get_ticker_from_db(self):
        ticker = 'SOLEUR'
        timestamp = '1672012800'
        print(data_requests.get_ticker_from_db(ticker, timestamp))

    def test_add_list_of_ohlc(self):
        start = 1609459200
        ticker_list = ['XBTEUR', 'ADAEUR', 'MATICEUR']
        print(data_requests.add_list_of_ohlc(ticker_list, start))



if __name__ == '__main__':
    unittest.main()

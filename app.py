import datetime

import numpy as np
import streamlit as st
import pandas as pd
import data_requests as data_requests
import matplotlib.pyplot as plt


def main():
    # Layout setup:
    st.set_page_config(page_title="Kraken Staking Calculator", page_icon=":chart_with_upwards_trend:", layout="wide")
    st.title("Kraken Staking Calculator")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    col1, col2, col3 = st.columns(3)
    with col1:
        base_currency = st.selectbox('Select base currency', ('EUR', 'USD'))
        # used to determine if asset is in base currency
        appendix = '_' + base_currency

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    with col2:
        start_date = st.date_input('Start date', today)
    with col3:
        end_date = st.date_input('End date', tomorrow)
    if start_date > end_date:
        st.error('Error: End date must fall after start date.')

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # preprocessing and interface check:
        # check if all required columns are in dataframe:
        required_columns = ["txid", "refid", "time", "type", "subtype", "aclass", "asset", "amount", "fee", "balance"]
        if not all(col in df.columns for col in required_columns):
            missing_columns = list(set(required_columns) - set(df.columns))
            st.warning("Dataframe is missing the following columns: " + ', '.join(
                missing_columns) + ". These columns are required to process the data.")
        else:
            # parse time to datetime objects (DatetimeIndex) in order to make time comparisons possible::
            try:
                # linux timestamps
                # df['time'] = pd.to_datetime(df['time']).map(pd.Timestamp.timestamp)
                # DatetimeIndex
                df['time'] = pd.to_datetime(df['time'])
            except ValueError:
                st.warning("An error occurred while trying to parse the 'time' column.")
            with st.expander("Raw Data"):
                st.dataframe(df)

            # filter raw dataframe such that only staking rewards are included:
            df = df.query('type.str.contains("staking")', engine='python')
            df = df.groupby(['time', 'asset']).sum().reset_index()
            rewards_df = df.pivot(index='time', columns='asset', values='amount')

            # Extract all column names which include staking rewards:
            reward_assets = [col for col in rewards_df.columns if '.S' in col]

            # min DatetimeIndex in rewards_df:
            min_datetime_index = rewards_df.index.min()

            # parse min_datetime_index to linux timestamp:
            date_format = '%Y-%m-%d %H:%M:%S'
            dt = pd.to_datetime(min_datetime_index, format=date_format)
            min_datetime_index_timestamp = dt.timestamp() - 172800  # 2 days earlier as buffer

            st.subheader("Fiat exchange and reward overview")

            if st.button("update exchange database"):
                # build correct ticker strings in order to request from kraken api:
                with st.spinner('Receiving data ...'):
                    ticker_list = []
                    for asset in reward_assets:
                        asset = asset.rstrip('.S')
                        asset = asset + base_currency
                        ticker_list.append(asset)
                    # update database with given ticker list:
                    data_requests.add_list_of_ohlc(ticker_list, min_datetime_index_timestamp)
                st.success("Updated: " + str(ticker_list) + " from last: " + str(dt))

            # Calculate accumulated rewards
            df_accumulated = rewards_df.cumsum()

            for col_name in reward_assets:
                new_col_name = col_name + appendix
                rewards_df[new_col_name] = np.nan
                df_accumulated[new_col_name] = np.nan

            # Value of each reward at receiving timestamp:
            for date, row in rewards_df.T.iteritems():
                for col, value in row.iteritems():
                    if not np.isnan(value):
                        # ticker:
                        ticker = col.rstrip('.S')
                        ticker = ticker + base_currency
                        # timestamp normalized to midnight:
                        date_normalized = date.normalize().timestamp()
                        # print(f"Date: {date} normalized: {date.normalize()}, Column: {col}, Value: {value}")
                        reward_in_base_currency = data_requests.get_ticker_from_db(ticker, date_normalized)
                        # print(reward_in_base_currency)
                        reward_in_base_currency_val = float(value) * float(reward_in_base_currency["close"])
                        rewards_df.at[date, col + appendix] = str(round(reward_in_base_currency_val, 2))

            # Development of value of accumulated rewards at timestamp:
            for date, row in df_accumulated.T.iteritems():
                for col, value in row.iteritems():
                    if not np.isnan(value):
                        # ticker:
                        ticker = col.rstrip('.S')
                        ticker = ticker + base_currency
                        # timestamp normalized to midnight:
                        date_normalized = date.normalize().timestamp()
                        # print(f"Date: {date} normalized: {date.normalize()}, Column: {col}, Value: {value}")
                        reward_in_base_currency = data_requests.get_ticker_from_db(ticker, date_normalized)
                        # print(reward_in_base_currency)
                        reward_in_base_currency_val = float(value) * float(reward_in_base_currency["close"])
                        df_accumulated.at[date, col + appendix] = str(round(reward_in_base_currency_val, 2))

            # display dataframes on frontend:
            with st.expander("Rewards: Reward in base currency is the value of received reward at timestamp"):
                st.dataframe(rewards_df)
            with st.expander("Accumulated Rewards: Reward in base currency is the value of total reward at timestamp"):
                st.dataframe(df_accumulated)

            for asset in reward_assets:
                # first date
                # last date
                from_date = df_accumulated.index.min()
                to_date = df_accumulated.index.max()
                st.subheader(str(asset))
                st.text("Received between " + str(from_date) + " - " + str(to_date))
                st.text("Total reward received: " + str(round(df_accumulated[asset].max(), 6)))
                # st.bar_chart(df_accumulated[asset])

                # Create figure and set axes for subplots
                plt.style.use('seaborn-white')

                plt.rcParams.update({'font.size': 4})

                fig = plt.figure()

                ax_rewards = fig.add_axes((0, 0.2, 1, 0.2))
                # Format x-axis ticks as dates
                ax_rewards.xaxis_date()
                rewards_df_only_values = rewards_df[asset].dropna()
                rewards_df_only_values_base_currency = rewards_df[asset + appendix].dropna()
                print(rewards_df_only_values)
                ax_rewards.plot(rewards_df_only_values.index, rewards_df_only_values,
                               alpha=0.5, label=asset, marker='o')
                ax_rewards.plot(rewards_df_only_values_base_currency.index, rewards_df_only_values_base_currency,
                               alpha=0.5, label=asset + appendix, marker='o')

                ax_rewards.legend(loc='lower left', fontsize='small', frameon=True, fancybox=True)
                ax_rewards.get_legend().set_title("on receive")

                ax_cummulated = fig.add_axes((0, 0.0, 1, 0.2), sharex=ax_rewards)
                # Format x-axis ticks as dates
                ax_cummulated.xaxis_date()
                accumulated_rewards_df_only_values = df_accumulated[asset].dropna()
                df_accumulated_base_currency = df_accumulated[asset + appendix].dropna()
                print(accumulated_rewards_df_only_values)
                ax_cummulated.plot(accumulated_rewards_df_only_values.index, accumulated_rewards_df_only_values,
                                   alpha=0.5, label=asset, marker='o')
                ax_cummulated.plot(df_accumulated_base_currency.index, df_accumulated_base_currency,
                                   alpha=0.5, label=asset + appendix, marker='o')
                ax_cummulated.legend(loc='lower left', fontsize='small', frameon=True, fancybox=True)
                ax_cummulated.get_legend().set_title("accumulated")

                st.pyplot(fig)


if __name__ == '__main__':
    main()

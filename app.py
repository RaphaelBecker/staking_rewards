import datetime
from sqlite3 import OperationalError

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

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=650)
    with col2:
        # kraken provides max 720 datapoints per request
        start_date = st.date_input('From date', start_date)
    with col3:
        end_date = st.date_input('To date', end_date)
    if start_date > end_date:
        st.error('Error: End date must fall after start date.')
        st.stop()

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
            min_datetime_index_normalized = min_datetime_index.normalize().timestamp()
            st.text(
                f"Min timestamp in provided csv: {min_datetime_index} App is able to process data from {start_date}")
            if min_datetime_index > start_date:
                st.warning(f"Kraken only provides max 720 days of historical data choose a earlier start date!")
                st.stop()


            # parse min_datetime_index to linux timestamp:
            min_datetime_index_timestamp = start_date - datetime.timedelta(days=1)  # 1 days earlier as buffer

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
                st.success("Updated: " + str(ticker_list) + " from last: " + str(start_date))


            # cut dataframe before start_date because database will only contian data later than start_date:
            # Create a boolean mask based on the comparison between the dates and the given date
            mask_rew = (rewards_df.index >= pd.to_datetime(start_date)) & (rewards_df.index <= pd.to_datetime(end_date))

            # Use the mask to select only the rows that are equal to or greater than the given date
            rewards_df = rewards_df[mask_rew]

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
                        try:
                            reward_in_base_currency = data_requests.get_ticker_from_db(ticker, date_normalized)
                        except:
                            st.warning("Database out of date. Please update database!")
                            st.stop()
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

            # Accumulate received asset in base currency on time of reward.
            # # Just as you would have sold the rewards immediately
            # Get columns with base_currency in their name
            columns_of_interest = [col for col in rewards_df.columns if base_currency in col]
            # Accumulate the values in the selected columns
            acc_df = rewards_df[columns_of_interest].astype(float).cumsum()
            # Rename the columns with "_ACC" suffix
            acc_df.columns = [col + '_ONREC' for col in acc_df.columns]
            # Concatenate the accumulated values with the original dataframe
            rewards_df = pd.concat([rewards_df, acc_df], axis=1)


            # display dataframes on frontend:
            with st.expander("Rewards: Reward in base currency is the value of received reward at timestamp"):
                st.dataframe(rewards_df)
            with st.expander("Accumulated Rewards: Reward in base currency is the value of total reward at timestamp"):
                st.dataframe(df_accumulated)

            for asset in reward_assets:
                try:
                    acc_worth = str(round(df_accumulated[asset + "_" + str(base_currency)].astype(float).dropna().iloc[-1], 6))
                    acc_on_sale_worth = str(round(rewards_df[asset + "_" + str(base_currency) + "_ONREC"].astype(float).dropna().iloc[-1], 6))
                except IndexError:
                    continue
                # first date
                # last date
                from_date = df_accumulated.index.min()
                to_date = df_accumulated.index.max()
                st.subheader(str(asset))
                st.text("Received between " + str(from_date) + " - " + str(to_date))
                st.text("Total reward received: " + str(round(df_accumulated[asset].max(), 6)) + ' ' + asset.rstrip('.S'))
                st.text("Worth last: " + acc_worth + " " + str(base_currency) + ". Worth on contiunous sale: " + acc_on_sale_worth + " " + str(base_currency))
                # st.bar_chart(df_accumulated[asset])

                # Create figure and set axes for subplots

                plt.rcParams.update({'font.size': 5})

                fig = plt.figure()

                ax_rewards_bar = fig.add_axes((0, 0.7, 1, 0.1))
                ax_cummulated_rewards = fig.add_axes((0, 0.6, 1, 0.1), sharex=ax_rewards_bar)
                ax_rewards_line = fig.add_axes((0, 0.4, 1, 0.2), sharex=ax_cummulated_rewards)

                rewards_df_only_values = rewards_df[asset].dropna()
                rewards_df_only_values_base_currency = rewards_df[asset + appendix].dropna()
                ax_rewards_bar.bar(rewards_df_only_values.index, rewards_df_only_values.astype(float),
                               alpha=0.5, label=asset)
                ax_rewards_line.plot(rewards_df_only_values_base_currency.index, rewards_df_only_values_base_currency.astype(float),
                               alpha=0.5, label=asset + appendix, marker='.')
                ax_rewards_line.yaxis.set_major_locator(plt.MaxNLocator(nbins=5, integer=True))

                ax_rewards_bar.legend(loc='best', fontsize='small', frameon=True, fancybox=True)
                ax_rewards_bar.get_legend().set_title("Rewards")
                ax_rewards_bar.set_ylabel(asset.rstrip('.S'), size=4)

                ax_rewards_line.legend(loc='best', fontsize='small', frameon=True, fancybox=True)
                ax_rewards_line.get_legend().set_title("Rewards in base currency")
                ax_rewards_line.set_ylabel(base_currency, size=4)

                ax_cummulated_rewards_base_currency = fig.add_axes((0, 0.0, 1, 0.4), sharex=ax_rewards_line)
                # Format x-axis ticks as dates
                ax_cummulated_rewards.xaxis_date()
                ax_cummulated_rewards_base_currency.xaxis_date()
                accumulated_rewards_df_only_values = df_accumulated[asset].dropna()
                # for comparison: Accumulated value of rewards on time of receive
                rewards_df_only_values_base_currency_accumulated = rewards_df[asset + "_" + base_currency + "_ONREC"].dropna()
                df_accumulated_base_currency = df_accumulated[asset + appendix].dropna()
                # calculate difference between value of accumulated rewards and gain on continuous sale of rewards:
                difference_df = df_accumulated_base_currency.astype(float) - rewards_df_only_values_base_currency_accumulated.astype(float)
                ax_cummulated_rewards.plot(accumulated_rewards_df_only_values.index, accumulated_rewards_df_only_values.astype(float),
                                   alpha=0.5, label=asset, marker='.')
                ax_cummulated_rewards_base_currency.plot(df_accumulated_base_currency.index, df_accumulated_base_currency.astype(float),
                                   alpha=0.5, label=asset + appendix, marker='.')
                ax_cummulated_rewards_base_currency.plot(rewards_df_only_values_base_currency_accumulated.index, rewards_df_only_values_base_currency_accumulated.astype(float),
                               alpha=0.5, label=asset + "_" + base_currency + "_ONSALE", marker='.')
                ax_cummulated_rewards_base_currency.axhline(y=0, color='grey', alpha=0.5, linestyle='-')
                ax_cummulated_rewards_base_currency.plot(difference_df.index, difference_df.astype(float),
                               alpha=0.5, label="DIFFERENCE", color='grey')

                ax_cummulated_rewards_base_currency.fill_between(difference_df.index, difference_df, 0, where=(difference_df >= 0), color='g', alpha=0.3)
                ax_cummulated_rewards_base_currency.fill_between(difference_df.index, difference_df, 0, where=(difference_df <= 0), color='r', alpha=0.3)


                ax_cummulated_rewards_base_currency.yaxis.set_major_locator(plt.MaxNLocator(nbins=10, integer=True))
                ax_cummulated_rewards.legend(loc='best', fontsize='small', frameon=True, fancybox=True)
                ax_cummulated_rewards.get_legend().set_title("Rewards accumulated")
                ax_cummulated_rewards.set_ylabel(asset.rstrip('.S'), size=4)
                ax_cummulated_rewards_base_currency.legend(loc='best', fontsize='small', frameon=True, fancybox=True)
                ax_cummulated_rewards_base_currency.get_legend().set_title("Value on continuous sale vs. on timestamp")
                ax_cummulated_rewards_base_currency.set_ylabel(base_currency, size=4)

                st.pyplot(fig)


if __name__ == '__main__':
    main()

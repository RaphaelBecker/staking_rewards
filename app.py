import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.set_page_config(page_title="Kraken Staking Calculator", page_icon=":chart_with_upwards_trend:", layout="wide")
    st.title("CSV to DataFrame")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    required_columns = ["txid", "refid", "time", "type", "subtype", "aclass", "asset", "amount", "fee", "balance"]

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        if not all(col in df.columns for col in required_columns):
            missing_columns = list(set(required_columns) - set(df.columns))
            st.warning("Dataframe is missing the following columns: " + ', '.join(missing_columns) + ". These columns are required to process the data.")
        else:
            try:
                # linux timestamps
                #df['time'] = pd.to_datetime(df['time']).map(pd.Timestamp.timestamp)
                # DatetimeIndex
                df['time'] = pd.to_datetime(df['time'])
                st.success("Time column parsed as datetime objects.")
            except ValueError:
                st.warning("An error occurred while trying to parse the 'time' column.")
            st.dataframe(df)

            df = df.query('type.str.contains("staking")', engine='python')
            df = df.groupby(['time', 'asset']).sum().reset_index()
            df = df.pivot(index='time', columns='asset', values='amount')

            df_accumulated = df.cumsum()
            st.dataframe(df_accumulated)

            columns_to_plot = [col for col in df_accumulated.columns if '.S' in col]
            # assets = df_accumulated['asset'].unique()
            for asset in columns_to_plot:
                if ".S" in asset:
                    # first date
                    # last date
                    from_date = df_accumulated.index.min()
                    to_date = df_accumulated.index.max()
                    st.subheader(str(asset))
                    st.text("Received between " + str(from_date) + " - " + str(to_date))
                    st.text("Total reward received: " + str(round(df_accumulated[asset].max(), 6)))
                    st.bar_chart(df_accumulated[asset])

            #assets = df['asset'].unique()
            #chart = st.line_chart()
            #for asset in assets:
            #    if ".S" in asset:
            #        df_asset = df[df['asset'] == asset]
            #        df_asset = df_asset.set_index('time')
            #        plt.plot(df_asset['amount'])
            #        plt.xlabel('time')
            #        plt.ylabel('amount')

                    # chart = st.line_chart(data=df_asset['amount'])


if __name__ == '__main__':
    main()
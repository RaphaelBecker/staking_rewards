import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.set_page_config(page_title="Kraken Staking Calculator", page_icon=":chart_with_upwards_trend:", layout="wide")
    st.title("CSV to DataFrame")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        required_columns = ["txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"]

        if not all(col in df.columns for col in required_columns):
            missing_columns = list(set(required_columns) - set(df.columns))
            st.warning("Dataframe is missing the following columns: " + ', '.join(missing_columns) + ". These columns are required to process the data.")
        else:
            try:
                df['time'] = pd.to_datetime(df['time'])
                st.success("Time column parsed as datetime objects.")
            except ValueError:
                st.warning("An error occurred while trying to parse the 'time' column.")
            st.dataframe(df)

            assets = df['asset'].unique()
            for asset in assets:
                if ".S" in asset:
                    df_asset = df[df['asset'] == asset]
                    df_asset = df_asset.set_index('time')
                    plt.plot(df_asset['amount'])
                    plt.xlabel('time')
                    plt.ylabel('amount')
                    plt.title(asset)
                    st.pyplot()


if __name__ == '__main__':
    main()
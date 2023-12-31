import glob
import pandas as pd
import numpy as np
import constants
import sqlite3
import pandas_ta as ta # noqa
from data_manipulation.strategy import macd_cum_diff_v1


def load_positions():
    # Create an empty list to store the dataframes
    dataframes = []

    # Get a list of all .csv files in the folder
    csv_files = glob.glob("data/*.csv")
    csv_files.remove("data/trades_directional_strategy_macd_.csv")

    # Iterate over each .csv file
    for file_path in csv_files:
        # Extract the trading pair from the filename
        trading_pair = file_path.split("_")[1]
        # Load the .csv file into a dataframe
        df0 = pd.read_csv(file_path)

        # Add the trading pair as a new column
        df0["Trading Pair"] = trading_pair

        # Append the dataframe to the list
        dataframes.append(df0)

    # Concatenate all dataframes into a single dataframe
    df = pd.concat(dataframes, ignore_index=True)
    df = df[df["timestamp"] >= constants.strategy_params["start_timestamp"] / 1000]
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
    df.sort_values("datetime", inplace=True)
    df["close_datetime"] = pd.to_datetime(df["close_timestamp"], unit="s")
    df["duration"] = (df["close_timestamp"] - df["timestamp"]) / 60
    df["side_num"] = df["side"].apply(lambda x: 1 if x == "TradeType.BUY" else -1)
    df["real_class"] = df["net_pnl_quote"].apply(lambda x: 1 if x > 0 else -1)
    df["race_id"] = (np.sign(df['net_pnl_quote']) != np.sign(df['net_pnl_quote'].shift()))
    df["race_id"] = df["race_id"].cumsum()
    df["race_status"] = df["real_class"].apply(lambda x: "Positive" if x > 0 else "Negative")
    # TODO: Check volume formula
    df["volume"] = df["amount"] * df["entry_price"]
    return df


def load_candles():
    candles = pd.read_csv("/home/drupman/PycharmProjects/download_candles/hummingbot/data/candles_DOGE-BUSD_5m.csv")
    candles = candles[(candles["timestamp"] >= constants.strategy_params["start_timestamp"]) & (candles["timestamp"] <= constants.strategy_params["end_timestamp"])]
    candles["datetime"] = pd.to_datetime(candles["timestamp"], unit="ms")
    candles = macd_cum_diff_v1(candles)
    candles.sort_values("datetime", inplace=True)
    return candles


def max_drawdown(df):
    # TODO: Calculate correct drawdown
    cumulative_returns = df["net_pnl_quote"].cumsum()
    peak = np.maximum.accumulate(cumulative_returns)
    drawdown = (cumulative_returns - peak)
    max_draw_down = np.min(drawdown)
    return max_draw_down


def get_market_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('data/directional_strategy_macd_diff.sqlite')

    # Get the list of table names in the database
    table_names = ['MarketData', '"Order"', 'TradeFill', 'OrderStatus']
    # Load each table into a dataframe
    dataframes = {}
    for table_name in table_names:  # Extract the table name from the result tuple
        query = f"SELECT * FROM {table_name};"
        dataframes[table_name] = pd.read_sql_query(query, conn)

    # Close the database connection
    conn.close()

    # Access the dataframes
    # for table_name, dataframe in dataframes.items():
    #     print(f"Table: {table_name}")
    #     print(dataframe)
    #     print()  # Empty line for separation

    candles_df = dataframes['MarketData']
    candles_df['datetime'] = pd.to_datetime(candles_df['timestamp'])
    candles_df.set_index('datetime', inplace=True)
    candles_df_5m = candles_df.resample('5T').agg({'mid_price': ['first', 'max', 'min', 'last']})
    candles_df_5m.columns = ['open', 'high', 'low', 'close']
    candles_df_5m = candles_df_5m / 1000000
    candles_df_5m.reset_index(inplace=True)
    candles = macd_cum_diff_v1(candles_df_5m)
    candles.sort_values("datetime", inplace=True)
    return candles
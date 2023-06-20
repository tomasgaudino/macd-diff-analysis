import pandas as pd
import numpy as np
import glob
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="MACD Cum Diff Performance", layout="wide")


def load_markets():
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
    return df


def max_drawdown(df):
    # TODO: Calculate correct drawdown
    cumulative_returns = df["net_pnl_quote"].cumsum()
    peak = np.maximum.accumulate(cumulative_returns)
    drawdown = (cumulative_returns - peak)
    max_drawdown = np.min(drawdown)
    return max_drawdown


strategy_params = {"directional_strategy_name": "MACD_DIFF_V1",
                   "trading_pair": "DOGE-BUSD",
                   "interval": "5m",
                   "exchange": "binance_perpetual",
                   "initial_portfolio": 150.0,
                   "start_timestamp": 1686754800000.0,
                   "order_amount_usd": 20.0,
                   "leverage": 20,
                   "stop_loss": 0.0075,
                   "take_profit": 0.1,
                   "time_limit": 60 * 55,
                   "trailing_stop_activation_delta": 0.0016,
                   "trailing_stop_trailing_delta": 0.001,
                   "delta_macd_thold": 0.0008,
                   "macdh_norm_thold": 0.0,
                   "target_thold": 0.0025}

candles = pd.read_csv("/home/drupman/PycharmProjects/download_candles/hummingbot/data/candles_DOGE-BUSD_5m.csv")
candles = candles[candles["timestamp"] >= strategy_params["start_timestamp"]]
candles["datetime"] = pd.to_datetime(candles["timestamp"], unit="ms")
candles.sort_values("datetime", inplace=True)

df = load_markets()
df = df[df["timestamp"] >= strategy_params["start_timestamp"] / 1000]
df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
df["duration"] = (df["close_timestamp"] - df["timestamp"]) / 60
df["side_num"] = df["side"].apply(lambda x: 1 if x == "TradeType.BUY" else -1)
# TODO: Check volume formula
df["volume"] = df["amount"] * df["entry_price"]
df.sort_values("datetime", inplace=True)

total_pnl = df["net_pnl_quote"].sum()
total_pnl_pct = total_pnl / strategy_params["initial_portfolio"]
total_positions = len(df)
total_volume = df["volume"].sum()
total_days_duration = (candles["timestamp"].max() / 1000 - df["timestamp"].min()) / (60 * 60 * 24)
profitable_pct = 100 * len(df[df["net_pnl_quote"] > 0]) / len(df)
profits = df.loc[df["net_pnl_quote"] > 0, "net_pnl_quote"]
loses = df.loc[df["net_pnl_quote"] <= 0, "net_pnl_quote"]
profit_factor = profits.sum() / loses.sum() if len(loses) > 0 else np.nan
max_draw_down = max_drawdown(df)
avg_profit = df["net_pnl_quote"].mean()
avg_duration = df["duration"].mean()
with st.sidebar:
    st.subheader("Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total profit", f"${total_pnl:.2f}", delta=f"{total_pnl_pct:.4f}%")
    with col2:
        st.metric("Total duration (days)", f"{total_days_duration:.2f}")
    st.subheader("Params")
    st.code(f"""
{"directional_strategy_name".upper()} = {strategy_params["directional_strategy_name"]}
{"trading_pair".upper()} = {strategy_params["trading_pair"]}
{"interval".upper()} = {strategy_params["interval"]}
{"exchange".upper()} = {strategy_params["exchange"]}
{"initial_portfolio".upper()} = {strategy_params["initial_portfolio"]}
{"start_timestamp".upper()} = {strategy_params["start_timestamp"]}
{"order_amount_usd".upper()} = {strategy_params["order_amount_usd"]}
{"leverage".upper()} = {strategy_params["leverage"]}
{"stop_loss".upper()} = {strategy_params["stop_loss"]}
{"take_profit".upper()} = {strategy_params["take_profit"]}
{"time_limit".upper()} = {strategy_params["time_limit"]}
{"trailing_stop_activation_delta".upper()} = {strategy_params["trailing_stop_activation_delta"]}
{"trailing_stop_trailing_delta".upper()} = {strategy_params["trailing_stop_trailing_delta"]}
{"delta_macd_thold".upper()} = {strategy_params["delta_macd_thold"]}
{"macdh_norm_thold".upper()} = {strategy_params["macdh_norm_thold"]}
{"target_thold".upper()} = {strategy_params["target_thold"]}
""")

main = make_subplots(rows=2,
                     shared_xaxes=True,
                     vertical_spacing=0.02,
                     row_heights=[600, 200],
                     x_title="Datetime (UTC)")
main.add_trace(go.Candlestick(name="Price (BUSD)",
                              x=candles["datetime"],
                              open=candles["open"],
                              high=candles["high"],
                              low=candles["low"],
                              close=candles["close"]),
               col=1,
               row=1)
main.add_trace(go.Scatter(name="Positions",
                          x=df["datetime"],
                          y=df["entry_price"],
                          mode="markers",
                          marker={"color": "yellow"},
                          ),
               col=1,
               row=1)
main.add_trace(go.Scatter(name="PnL (BUSD)",
                          x=df["datetime"],
                          y=df["net_pnl_quote"].cumsum(),
                          fill="tozeroy",
                          fillcolor="lightblue",
                          opacity=0.2),
               col=1,
               row=2)
main.update_layout(xaxis_rangeslider_visible=False,
                   height=900)

st.title('MACD Cum Diff V1 results')
st.subheader('Metrics')
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col1:
    st.metric("Total volume", f"${total_volume:.1f}")
with col2:
    st.metric("N° Positions", f"{total_positions}")
with col3:
    st.metric("% Profitable", f"{profitable_pct:.2f}%")
with col4:
    st.metric("Profit factor", f"{profit_factor:.2f}" if profit_factor != np.nan else "-")
with col5:
    st.metric("Max Draw Down", f"${max_draw_down:.2f}")
with col6:
    st.metric("Avg Profit", f"${avg_profit:.3f}")
with col7:
    st.metric("Avg Min Duration", f"{avg_duration:.1f}")

st.subheader('Market activity and PnL')
st.plotly_chart(main, use_container_width=True)
st.subheader('Close types')
df_grouped_by_close_type_and_side = df.groupby(["close_type", "side"]).size().reset_index(name="side_count")
col1, col2 = st.columns(2)
with col1:
    fig = px.bar(df_grouped_by_close_type_and_side, x="side_count", y="close_type", color="side", orientation="h", labels="side_count")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.bar(df_grouped_by_close_type_and_side, x="side", y="side_count", color="close_type")
    st.plotly_chart(fig, use_container_width=True)








a = 1

import numpy as np
import pandas as pd
import streamlit as st
import constants
from data_manipulation.preprocessing import load_positions, get_market_data, max_drawdown
from data_viz.utils import get_strategy_params
from data_viz.position import PositionsExecuted

st.set_page_config(page_title="MACD Cum Diff Performance", layout="wide")

strategy_params = constants.strategy_params
df = load_positions()
candles = get_market_data()

total_pnl = df["net_pnl_quote"].sum()
total_pnl_pct = 100 * total_pnl / strategy_params["initial_portfolio"]
total_positions = len(df)
total_volume = df["volume"].sum()
total_days_duration = (candles["datetime"].max() - df["datetime"].min()).total_seconds() / (24 * 60 * 60)
profitable_pct = 100 * len(df[df["net_pnl_quote"] > 0]) / len(df)
profits = df.loc[df["net_pnl_quote"] > 0, "net_pnl_quote"]
loses = df.loc[df["net_pnl_quote"] <= 0, "net_pnl_quote"]
profit_factor = profits.sum() / loses.sum() if len(loses) > 0 else np.nan
max_draw_down = max_drawdown(df)
avg_profit = df["net_pnl_quote"].mean()
avg_duration = df["duration"].mean()

with st.sidebar:
    st.subheader("Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total profit", f"${total_pnl:.2f}", delta=f"{total_pnl_pct:.4f}%")
    with col2:
        st.metric("Total duration (days)", f"{total_days_duration:.2f}")
    st.subheader("Params")
    st.code(get_strategy_params())


st.title('MACD Cum Diff V1 results')
st.subheader('Summary metrics')
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

st.markdown("<hr>", unsafe_allow_html=True)
positions = PositionsExecuted(df, candles)

st.subheader('Close types')
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(positions.get_close_type_by_side(), use_container_width=True)
with col2:
    st.plotly_chart(positions.get_side_by_close_type(), use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.subheader('Streaks')
st.plotly_chart(positions.plot_streaks(), use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.subheader('Market activity and PnL')

dates = df["datetime"].dt.date.unique()
show_market_activity = st.checkbox("Show market activity", False)
if show_market_activity:
    subset_by_date = st.checkbox("Subset by date", True)
    if subset_by_date:
        selected_date = st.slider("Select Date", value= min(dates), min_value=min(dates), max_value=max(dates))

        # Subset the dataframe based on the selected date
        subset_df = df[df["datetime"].dt.date == selected_date]
        subset_candles = candles[candles["datetime"].dt.date == selected_date]
        positions = PositionsExecuted(subset_df, subset_candles)

    st.plotly_chart(positions.main_chart(), use_container_width=True)
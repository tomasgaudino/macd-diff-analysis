import pandas as pd
import numpy as np


def macd_cum_diff_v1(candles_df):
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    candles_df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal, append=True)

    macdh = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal}'
    macdh_norm = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal}_norm'
    candles_df[macdh_norm] = candles_df[macdh] / candles_df['close']

    candles_df['diff'] = candles_df[macdh_norm].diff()
    candles_df['start'] = np.sign(candles_df['diff']) != np.sign(candles_df['diff'].shift())
    candles_df['id'] = candles_df['start'].cumsum()
    candles_df['cum_macd_filtered'] = candles_df.groupby('id')['diff'].cumsum()

    candles_df['target'] = candles_df['close'].rolling(100).std() / candles_df['close']
    return candles_df

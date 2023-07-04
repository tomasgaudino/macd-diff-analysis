import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import constants


class PositionsExecuted:
    def __init__(self, df, candles):
        self.df = df
        self.candles = candles
        self.df_grouped_by_close_type_and_side = df.groupby(["close_type", "side"]).size().reset_index(name="side_count")
        self.macd_cum_thold = constants.strategy_params["delta_macd_thold"]
        self.base_figure = make_subplots(rows=5, shared_xaxes=True,
                                         vertical_spacing=0.02,
                                         row_heights=[600, 200, 200, 200, 200],
                                         x_title="Datetime (UTC)",
                                         subplot_titles=("OHLC 5m", "MACD Histogram Norm / MACD Cum Diff", "Target", "Cum Net PnL (BUSD)", "Cum Trade PnL (BUSD)"))

    def main_chart(self):
        self.base_figure.add_trace(go.Candlestick(name="Price (BUSD)",
                                   x=self.candles["datetime"],
                                   open=self.candles["open"],
                                   high=self.candles["high"],
                                   low=self.candles["low"],
                                   close=self.candles["close"]),
                                   col=1,
                                   row=1)
        self.add_target()
        self.add_pnl()
        self.add_macd()
        self.add_positions()
        self.update_layout()
        return self.base_figure

    def update_layout(self):
        self.base_figure.update_layout(xaxis_rangeslider_visible=False,
                                       height=900)

    def add_target(self):
        row_number = 3
        self.base_figure.add_trace(go.Scatter(x=self.candles.datetime,
                                              y=self.candles.target,
                                              name='target'),
                                   col=1,
                                   row=row_number)
        self.base_figure.add_hline(y=0.0045, row=row_number, line_dash="dot", line_color='gray')

    def add_pnl(self):
        self.base_figure.add_trace(go.Scatter(name="Net PnL (BUSD)",
                                              x=self.df["datetime"],
                                              y=self.df["net_pnl_quote"].cumsum()),
                                   col=1,
                                   row=4)

        self.base_figure.add_trace(go.Scatter(name="Trade PnL (BUSD)",
                                              x=self.df["datetime"],
                                              y=self.df["trade_pnl_quote"].cumsum()),
                                   col=1,
                                   row=5)

    def add_positions(self):
        self.df.loc[self.df['side_num'] == -1, 'fig'] = 'triangle-down'
        self.df.loc[self.df['side_num'] == 1, 'fig'] = 'triangle-up'
        self.df.loc[self.df['real_class'] == 1, 'color'] = 'lightgreen'
        self.df.loc[self.df['real_class'] == -1, 'color'] = 'red'
        self.base_figure.add_trace(go.Scatter(x=self.df.loc[(self.df['side'] != 0), 'datetime'],
                                              y=self.df.loc[self.df['side'] != 0, 'entry_price'],
                                              name='Entry Price: $',
                                              mode='markers',
                                              marker_color=self.df.loc[(self.df['side'] != 0), 'color'],
                                              marker_symbol=self.df.loc[(self.df['side'] != 0), 'fig'],
                                              marker_size=20,
                                              marker_line={'color': 'black', 'width': 0.7}))

        for index, row in self.df.iterrows():
            self.base_figure.add_shape(type="rect",
                                       fillcolor="green",
                                       opacity=0.5,
                                       x0=row.datetime,
                                       y0=row.entry_price,
                                       x1=row.close_datetime,
                                       y1=row.entry_price * (1 + (row.tp * row.side_num)),
                                       line=dict(color="green"))
            # Add SL
            self.base_figure.add_shape(type="rect",
                                       fillcolor="red",
                                       opacity=0.5,
                                       x0=row.datetime,
                                       y0=row.entry_price,
                                       x1=row.close_datetime,
                                       y1=row.entry_price * (1 - row.sl * row.side_num),
                                       line=dict(color="red"))

    def add_macd(self, slow=12, fast=26, signal=9, show_macd_and_signal=True):
        df = self.candles.copy()
        row_number = 2
        if show_macd_and_signal:
            self.base_figure.add_trace(go.Scatter(x=df['datetime'],
                                                  y=df[f'MACD_{slow}_{fast}_{signal}'],
                                                  name="MACD",
                                                  marker_color="#DF9828"),
                                       row=row_number,
                                       col=1)

            self.base_figure.add_trace(go.Scatter(x=df['datetime'],
                                                  y=df[f'MACDs_{slow}_{fast}_{signal}'],
                                                  name="Signal",
                                                  marker_color="#352B9B"),
                                       row=row_number,
                                       col=1)

        # Add the MACD histogram to the lower subplot
        self.base_figure.add_trace(go.Bar(x=df['datetime'],
                                          y=df[f'MACDh_{slow}_{fast}_{signal}_norm'],
                                          marker=dict(color=df[f'MACDh_{slow}_{fast}_{signal}_norm'].apply(lambda x: '#F4DEB6' if x >= 0 else '#C75959')),
                                          name="MACD Hist"),
                                   row=row_number,
                                   col=1)

        self.base_figure.add_trace(go.Bar(x=df['datetime'],
                                          y=df[f'cum_macd_filtered'],
                                          marker_color='#448BCC',
                                          name="Delta MACD"),
                                   row=row_number,
                                   col=1)

        self.base_figure.add_hline(y=self.macd_cum_thold, line_dash="dot", row=row_number, line_color='gray')
        self.base_figure.add_hline(y=-self.macd_cum_thold, line_dash="dot", row=row_number, line_color='gray')

    def plot_streaks(self):
        color_discrete_map = {'Negative': 'red', 'Positive': 'lightgreen'}
        streaks = self.df.groupby(["race_id", "race_status"])["net_pnl_quote"].count().reset_index().rename(columns={'net_pnl_quote': 'length'})
        return px.histogram(streaks,
                            x="length",
                            color='race_status',
                            barmode='group',
                            text_auto=True,
                            color_discrete_map=color_discrete_map)

    def get_side_by_close_type(self):
        color_discrete_map = {'CloseType.STOP_LOSS': 'red', 'CloseType.TAKE_PROFIT': 'lightgreen'}
        return px.bar(self.df_grouped_by_close_type_and_side,
                      x="side_count",
                      y="side",
                      color="close_type",
                      orientation="h",
                      text_auto=True,
                      color_discrete_map=color_discrete_map)

    def get_close_type_by_side(self):
        return px.bar(self.df_grouped_by_close_type_and_side,
                      x="side_count",
                      y="close_type",
                      color="side",
                      orientation="h",
                      text_auto=True)

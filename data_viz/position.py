import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class PositionsExecuted:
    def __init__(self, df, candles, tp_viz_factor=1.0):
        self.df = df
        self.candles = candles
        self.df_grouped_by_close_type_and_side = df.groupby(["close_type", "side"]).size().reset_index(name="side_count")
        self.tp_viz_factor = tp_viz_factor

    def main_chart(self):
        fig = make_subplots(rows=2,
                            shared_xaxes=True,
                            vertical_spacing=0.02,
                            row_heights=[600, 200],
                            x_title="Datetime (UTC)")
        fig.add_trace(go.Candlestick(name="Price (BUSD)",
                                     x=self.candles["datetime"],
                                     open=self.candles["open"],
                                     high=self.candles["high"],
                                     low=self.candles["low"],
                                     close=self.candles["close"]),
                      col=1,
                      row=1)
        fig.add_trace(go.Scatter(name="PnL (BUSD)",
                                 x=self.df["datetime"],
                                 y=self.df["net_pnl_quote"].cumsum(),
                                 fill="tozeroy",
                                 fillcolor="lightblue",
                                 opacity=0.2),
                      col=1,
                      row=2)
        fig.update_layout(xaxis_rangeslider_visible=False,
                          height=900)
        fig = self.add_positions(fig)
        return fig

    def get_close_type_by_side(self):
        return px.bar(self.df_grouped_by_close_type_and_side,
                      x="side_count",
                      y="close_type",
                      color="side",
                      orientation="h")

    def get_side_by_close_type(self):
        return px.bar(self.df_grouped_by_close_type_and_side,
                      x="side_count",
                      y="side",
                      color="close_type",
                      orientation="h")

    def add_positions(self, base_figure):
        self.df.loc[self.df['side_num'] == -1, 'fig'] = 'triangle-down'
        self.df.loc[self.df['side_num'] == 1, 'fig'] = 'triangle-up'
        self.df.loc[self.df['real_class'] == 1, 'color'] = 'lightgreen'
        self.df.loc[self.df['real_class'] == -1, 'color'] = 'red'
        base_figure.add_trace(go.Scatter(x=self.df.loc[(self.df['side'] != 0), 'datetime'],
                                         y=self.df.loc[self.df['side'] != 0, 'entry_price'],
                                         name='Entry Price: $',
                                         mode='markers',
                                         marker_color=self.df.loc[(self.df['side'] != 0), 'color'],
                                         marker_symbol=self.df.loc[(self.df['side'] != 0), 'fig'],
                                         marker_size=20,
                                         marker_line={'color': 'black', 'width': 0.7}))

        for index, row in self.df.iterrows():
            tp = row.tp * self.tp_viz_factor
            base_figure.add_shape(type="rect",
                                  fillcolor="green",
                                  opacity=0.5,
                                  x0=row.datetime,
                                  y0=row.entry_price,
                                  x1=row.close_datetime,
                                  y1=row.entry_price * (1 + (tp) * row.side_num),
                                  line=dict(color="green"))
            # Add SL
            base_figure.add_shape(type="rect",
                                  fillcolor="red",
                                  opacity=0.5,
                                  x0=row.datetime,
                                  y0=row.entry_price,
                                  x1=row.close_datetime,
                                  y1=row.entry_price * (1 - row.sl * row.side_num),
                                  line=dict(color="red"))
        return base_figure

    def add_macd(self, slow=12, fast=26, signal=9):
        df = self.candles.copy()
        # df.ta.macd(slow=slow, fast=fast, signal=signal, append=True)
        # Add MACD with signal to lower subplot
        self.base_figure.add_trace(go.Scatter(x=df['timestamp'],
                                              y=df[f'MACD_{slow}_{fast}_{signal}'],
                                              name="MACD",
                                              marker_color="blue"),
                                   row=3,
                                   col=1)

        self.base_figure.add_trace(go.Scatter(x=df['timestamp'],
                                              y=df[f'MACDs_{slow}_{fast}_{signal}'],
                                              name="Signal",
                                              marker_color="red"),
                                   row=3,
                                   col=1)

        # Add the MACD histogram to the lower subplot
        self.base_figure.add_trace(go.Bar(x=df['timestamp'],
                                          y=df[f'MACDh_{slow}_{fast}_{signal}_norm'],
                                          marker=dict(color=df[f'MACDh_{slow}_{fast}_{signal}_norm'].apply(lambda x: 'lightgreen' if x >= 0 else 'red')),
                                          name="MACD Hist"),
                                   row=3,
                                   col=1)

        self.base_figure.add_trace(go.Bar(x=df['timestamp'],
                                          y=df[f'cum_macd_filtered'],
                                          marker_color='aqua',
                                          name="Delta MACD"),
                                   row=3,
                                   col=1)
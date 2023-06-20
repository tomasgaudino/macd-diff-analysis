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
        fig.add_trace(go.Scatter(name="Positions",
                                 x=self.df["datetime"],
                                 y=self.df["entry_price"],
                                 mode="markers",
                                 marker={"color": "yellow"},
                                 ),
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

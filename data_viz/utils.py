import constants
import pandas as pd


def get_strategy_params():
    strategy_params = constants.strategy_params.copy()
    return f"""
# Market data
{"directional_strategy_name".upper()} = {strategy_params["directional_strategy_name"]}
{"trading_pair".upper()} = {strategy_params["trading_pair"]}
{"interval".upper()} = {strategy_params["interval"]}
{"exchange".upper()} = {strategy_params["exchange"]}

# Strategy settings
{"initial_portfolio".upper()} = {strategy_params["initial_portfolio"]}
{"start_timestamp".upper()} = {pd.to_datetime(strategy_params["start_timestamp"], unit='ms')}
{"order_amount_usd".upper()} = {strategy_params["order_amount_usd"]}
{"leverage".upper()} = {strategy_params["leverage"]}

# Position config
{"std_span".upper()} = {strategy_params["std_span"]}
{"stop_loss_multiplier".upper()} = {strategy_params["stop_loss_multiplier"]}
{"take_profit_multiplier".upper()} = {strategy_params["take_profit_multiplier"]}
{"time_limit".upper()} = {strategy_params["time_limit"]}
{"trailing_stop_activation_delta".upper()} = {strategy_params["trailing_stop_activation_delta"]}
{"trailing_stop_trailing_delta".upper()} = {strategy_params["trailing_stop_trailing_delta"]}

# Strategy config
{"delta_macd_thold".upper()} = {strategy_params["delta_macd_thold"]}
{"macdh_norm_thold".upper()} = {strategy_params["macdh_norm_thold"]}
{"target_thold".upper()} = {strategy_params["target_thold"]}
"""

import constants


def get_strategy_params():
    strategy_params = constants.strategy_params.copy()
    return f"""
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
"""

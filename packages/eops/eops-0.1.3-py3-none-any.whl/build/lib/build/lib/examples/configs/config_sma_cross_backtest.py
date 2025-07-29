# examples/configs/config_sma_cross_backtest.py

# 导入你刚刚编写的策略类
from examples.strategies.ema_cross import SmaCrossStrategy

# --- 策略配置 ---
# 你的策略类
STRATEGY_CLASS = SmaCrossStrategy

# 传递给你策略的参数
STRATEGY_PARAMS = {
    "symbol": "BTC-USDT-SWAP", # 注意：要和你的数据文件名中的 symbol 一致
    "short_window": 20,
    "long_window": 50,
    "trade_amount": 0.1 # 每次交易 0.1 个 BTC
}

# --- 回测引擎配置 ---
ENGINE_PARAMS = {
    "initial_cash": 1000.0, # 初始资金 10,000 USD
    "fee_rate": 0.0008       # 交易手续费，例如 0.08%
}

# --- 数据配置 ---
# 指定用于回测的数据文件路径
# 这个路径是相对于你执行 `eops` 命令的根目录
BACKTEST_DATA_PATH = "./data/okx_BTC-USDT-SWAP_1h.csv"

# (实盘交易用的配置，这里留空)
# EXCHANGE_CLASS = ...
# EXCHANGE_PARAMS = ...
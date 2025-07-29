# examples/configs/ema_cross_backtest.py
from examples.strategies.ema_cross import EmaCrossStrategy

# 1. 指定运行模式 
MODE = 'backtest'

# 2. 指定策略类
STRATEGY_CLASS = EmaCrossStrategy

# 3. 回测特定参数
BACKTEST_PARAMS = {
    # 使用 `eops data download` 命令下载的数据文件
    "data_path": "./data/binance_BTC_USDT_1h.csv", 
    "initial_cash": 10000.0,
    "fee_rate": 0.001,
    # (可选) 指定回测报告的保存路径
    "report_path": "./reports/ema_cross_backtest_report.html" 
}

# 4. 策略特定参数
STRATEGY_PARAMS = {
    # 注意：这里我们使用兼容模式的 symbol，因为数据文件名是这样。
    # 在真实回测中，数据文件也应该用 EID 命名，或在策略中做转换。
    "instrument_id": "BTC/USDT", 
    "timeframe": "1h",
    "short_ema": 10,
    "long_ema": 20,
    "order_amount": 0.1 # 每次交易0.1个BTC
}
# Auto-generated wrapper for instance 1
from pathlib import Path
from ema_cross_backtest import *

BACKTEST_PARAMS.update({'data_path': '/Users/ops/Desktop/dashboard/dashboard/market_data/binance_BTC_USDT_1h.csv', 'initial_cash': 10000.0, 'fee_rate': 0.001, 'report_path': './reports/ema_cross_backtest_report.html'})
MODE = 'backtest'
STRATEGY_PARAMS.update({'instrument_id': 'BTC/USDT', 'timeframe': '1h', 'short_ema': 10, 'long_ema': 20, 'order_amount': 0.1})
LOG_FILE = '/Users/ops/Desktop/dashboard/dashboard/logs/instance_1.log'

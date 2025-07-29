# Auto-generated wrapper for instance 8
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
try:
    from configs.ema_cross_backtest import *
except ImportError as e:
    raise ImportError(f"Could not import from 'configs.ema_cross_backtest'. Error: {e}")
MODE = 'backtest'
STRATEGY_PARAMS = {**(globals().get('STRATEGY_PARAMS', {})), **{"instrument_id": "BTC/USDT", "timeframe": "1h", "short_ema": 10, "long_ema": 20, "order_amount": 0.1}}
BACKTEST_PARAMS = {'data_path': '/Users/ops/Desktop/dashboard/dashboard/market_data/okx_BTC-USDT-SWAP_1h.csv', 'initial_cash': 10000.0}

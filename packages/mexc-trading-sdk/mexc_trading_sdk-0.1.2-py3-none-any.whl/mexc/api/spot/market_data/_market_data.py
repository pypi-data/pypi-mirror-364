from dataclasses import dataclass
from .time import Time
from .depth import Depth
from .trades import Trades
from .agg_trades import AggTrades
from .candles import Candles

@dataclass
class MarketData(
  Time,
  Depth,
  Trades,
  AggTrades,
  Candles,
):
  ...
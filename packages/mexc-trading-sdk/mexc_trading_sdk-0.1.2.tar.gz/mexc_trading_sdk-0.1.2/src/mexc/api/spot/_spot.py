from dataclasses import dataclass
from .trading import Trading
from .user_data import UserData
from .market_data import MarketData

@dataclass
class Spot(
  Trading,
  UserData,
  MarketData,
):
  ...
from dataclasses import dataclass, field
from mexc.core import MEXC_FUTURES_API_BASE
from .spot import Spot
from .wallet import Wallet
from .futures import Futures

@dataclass
class MEXC(Spot, Wallet):
  futures_api_base: str = field(default=MEXC_FUTURES_API_BASE, kw_only=True)

  def __post_init__(self):
    self.futures = Futures(client=self.client, base_url=self.futures_api_base)

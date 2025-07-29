from ._api import MEXC
from .spot import Spot
from .wallet import Wallet
from .futures import Futures
from . import spot, wallet, futures

__all__ = [
  'MEXC',
  'Spot', 'Wallet', 'Futures',
  'spot', 'wallet', 'futures',
]
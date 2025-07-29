from dataclasses import dataclass
from .my_trades import MyTrades
from .account import Account

@dataclass
class UserData(
  MyTrades,
  Account,
):
  ...
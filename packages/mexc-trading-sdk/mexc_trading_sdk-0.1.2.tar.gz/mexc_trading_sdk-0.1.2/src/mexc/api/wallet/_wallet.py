from .currency_info import CurrencyInfo
from .deposit_addresses import DepositAddresses
from .withdraw import Withdraw
from .cancel_withdraw import CancelWithdraw

class Wallet(CurrencyInfo, DepositAddresses, Withdraw, CancelWithdraw):
  ...
from typing_extensions import Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import trading_sdk as tdk
import mexc
from mexc.core import timestamp

@dataclass
class UserData(tdk.UserData):
  client: mexc.api.spot.UserData
  validate: bool = True

  @classmethod
  def new(cls, api_key: str, api_secret: str, *, validate: bool = True):
    return cls(
      client=mexc.api.spot.UserData(api_key=api_key, api_secret=api_secret),
      validate=validate,
    )

  async def my_trades(
    self, symbol: str, *, limit: int | None = None,
    start: datetime | None = None, end: datetime | None = None,
    start_id: str | None = None
  ) -> Sequence[tdk.UserData.Trade]:
    trades = await self.client.my_trades(symbol, limit=limit, start=start, end=end)
    match trades:
      case list(trades):
        return [
          tdk.UserData.Trade(
            id=t['id'],
            price=Decimal(t['price']),
            quantity=Decimal(t['qty']),
            time=timestamp.parse(t['time']),
            buyer=t['isBuyer'],
            maker=t['isMaker'],
          )
          for t in reversed(trades)
        ]
      case err:
        raise RuntimeError(err)


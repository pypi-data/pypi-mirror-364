from dataclasses import dataclass
from .place_order import PlaceOrder
from .edit_order import EditOrder
from .query_order import QueryOrder
from .query_all_orders import QueryAllOrders
from .cancel_order import CancelOrder
from .cancel_all_orders import CancelAllOrders

@dataclass
class Trading(
  PlaceOrder,
  EditOrder,
  CancelOrder,
  QueryOrder,
  QueryAllOrders,
  CancelAllOrders,
):
  ...
from dataclasses import dataclass, field
from urllib.parse import urlencode, quote
import hashlib
import hmac
from .client import ClientMixin, MEXC_FUTURES_API_BASE

def sign(payload: str, *, secret: str) -> str:
  return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

@dataclass
class AuthedMixin(ClientMixin):
  api_key: str
  api_secret: str

  @property
  def headers(self) -> dict:
    return { 'X-MEXC-APIKEY': self.api_key }

  def sign(self, query_string: str) -> str:
    return sign(query_string, secret=self.api_secret)
  
  def signed_query(self, params: dict) -> str:
    def fix(v):
      # fix bools, which would show otherwise as "hello=True" instead of "hello=true"
      if isinstance(v, bool):
        return str(v).lower()
      else:
        return v
    fixed_params = [(k, fix(v)) for k, v in params.items()]
    query = urlencode(fixed_params, quote_via=quote)
    return query + '&signature=' + self.sign(query)
  
  async def authed_request(
    self, method: str, path: str, params: dict = {}, *,
    json: dict | None = None,
  ):
    return await self.request(method, path, headers=self.headers, params=params, json=json)
  
  async def signed_request(self, method: str, path: str, params: dict = {}):
    return await self.request(method, path + '?' + self.signed_query(params), headers=self.headers)
  
@dataclass
class FuturesAuthedMixin(AuthedMixin):
  base_url: str = field(default=MEXC_FUTURES_API_BASE, kw_only=True)
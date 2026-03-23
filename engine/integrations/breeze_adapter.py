from __future__ import annotations

from dataclasses import dataclass
from datetime import timezone, datetime as dt
from typing import Any, Callable, Dict, Iterable, Optional

from engine.market.tick import MarketTick
from engine.utils.time import IST, now_ist

@dataclass(frozen=True)
class BreezeSubscription:  #Represents a breeze market data subscription request
    
    stock_token: str
    exchange_code: str = "NSE"
    product_type: str #change later to enums
    interval: str = "1second"
    
class BreezeAdapter: 
    """
    Normalizes Breeze ticks into internal MarketTick objects
    - Doesn't use SDK so that we can unit test without live dependency
    - Any object with compatible methods (ws_connect, subscribe_feeds) can be injected as 'client'
    """
    
    def __init__(self, 
                 client: Any, 
                 symbol_mapper: Optional[Callable[[str],str]]=None): #the mapper can be a function which takes a string, returns a tring or it can be None
        
        self.client = client
        self.symbol_mapper = symbol_mapper or (lambda symbol: symbol) #either use the defined mapper function as the mapper or just return (do nothing) the string (symbol entered) 
    
    def connect(self) -> None:
        if hasattr(self.client, "ws_connect"): #checks whether the client has the ws_connect attribute, and connects to the ws session if it does
            self.client.ws_connect()
    
    def subscribe(self, subscriptions: Iterable[BreezeSubscription]) -> None:
        
        for sub in subscriptions:
            self.client.subscribe_feeds(
                stock_token = sub.stock_token,
                exchange_code = sub.exchange_code,
                product_type = sub.product_type,
                interval = sub.interval
            )
    
    def normalize_tick(self, payload: Dict[str, Any]) -> MarketTick: #convert breeze tick into internal MarketTick object

        symbol = self._pick(payload, "symbol", "stock_code", "stock_name")
        bid = self._to_float(self._pick(payload, "best_bid_price", "bid", "b_price"))
        ask = self._to_float(self._pick(payload, "best_offer_price", "ask", "a_price"))
        ltp = self._to_float(self._pick(payload, "last_traded_price", "ltp", "close"))
        timestamp = self._parse_timestamp(
            self._pick(payload, "ltt", "timestamp", "exchange_time", "time", required=False)
        )

        return MarketTick(
            symbol=self.symbol_mapper(str(symbol)),
            bid=bid,
            ask=ask,
            ltp=ltp,
            tiemstamp=timestamp,
        )

    def _pick(self, payload: Dict[str, Any], *keys: str, required: bool = True) -> Any: 
        """
        Try multiple possible keys in a payload and return the first non-empty one
        """
        
        for key in keys:
            if key in payload and payload[key] not in (None, ""):
                return payload[key]

        if required:
            raise ValueError(f"Missing required field. Tried keys: {keys}")

        return None

    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid numeric value: {value!r}") from exc
    
    @staticmethod
    def _parse_timestamp(value: Any) -> dt:
        """Parse supported timestamp formats to timezone-aware IST datetime."""
        
        if value is None:
            return now_ist()

        if isinstance(value, dt):
            if value.tzinfo is None:
                return value.replace(tzinfo=IST)
            return value.astimezone(IST)

        if isinstance(value, (int, float)):
            ts = float(value)
            if ts > 1_000_000_000_000:  # milliseconds epoch
                ts /= 1000.0
            return dt.fromtimestamp(ts, tz=IST)

        if isinstance(value, str):
            value = value.strip()
            if value.isdigit():
                return BreezeAdapter._parse_timestamp(int(value))

            # Accept ISO strings like 2024-01-01T09:15:00+05:30 or with Z.
            try:
                parsed = dt.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    return parsed.replace(tzinfo=IST)
                return parsed.astimezone(IST)
            except ValueError:
                pass

        raise ValueError(f"Unsupported timestamp format: {value!r}")
from dataclasses import dataclass, field
from engine.utils.time import now_ist
from datetime import datetime as dt

from engine.core.enums import (OrderSide, InstrumentType, TradeSource)

@dataclass (frozen=True)
class Trade:
    trade_id: str
    order_id: str
    
    symbol: str
    instrument_type: InstrumentType
    
    side:OrderSide
    quantity: int
    price: float
    
    source: TradeSource
    
    timestamp: dt = field(default_factory=now_ist)
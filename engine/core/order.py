from dataclasses import dataclass, field
from datetime import datetime as dt
from typing import Optional

from engine.core.enums import (OrderSide,OrderType,OrderValiditity,OrderStatus,InstrumentType,TradeSource)
from engine.utils.time import now_ist


@dataclass
class Order:
    #Identity
    order_id: str
    symbol: str
    instrument_type: InstrumentType
    
    #core instant
    side: OrderSide
    order_type : OrderType
    quantity: int
    
    #input pricing depends on ordertype
    price: Optional[float]=None
    trigger_price: Optional[float]=None # for StopLoss orders
    
    #Metadata
    validity: OrderValiditity = OrderValiditity.GTC
    source: TradeSource = TradeSource.MANUAL
    
    #state
    status: OrderStatus = OrderStatus.PENDING
    
    #execution tracking
    filled_quantity: int=0
    average_fill_price: Optional[float]=None
    
    #timestamps
    created_at: dt = field(default_factory=now_ist)
    updated_at: dt = field(default_factory=now_ist)
    
    
    def remaining_quantity(self) -> int:
        return self.quantity - self.filled_quantity
    
    def is_open(self) -> bool: #if order is open still
        return self.status in {OrderStatus.PENDING,OrderStatus.OPEN}
    
    def is_terminal(self) -> bool: #whether order was executed, cancelled or rejected (not open anymore)
        return self.status in {
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED
        }
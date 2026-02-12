from typing import Optional
from uuid import uuid4

from engine.core.order import Order
from engine.core.trade import Trade
from engine.core.enums import OrderType,OrderSide, OrderStatus
from engine.market.tick import MarketTick

class Matcher:
    def match(self,order:Order, tick:MarketTick) -> Optional[Trade]:
        if order.symbol != tick.symbol:
            return None
        
        if not order.is_open():
            return None

        if order.order_type == OrderType.MARKET:
            fill_price = tick.ask if order.side == OrderSide.BUY else tick.bid
            return self._create_trade(order,fill_price)
        
        if order.order_type == OrderType.LIMIT:
            if order.side == OrderSide.BUY and tick.ask <= order.price:
                return self._create_trade(order, order.price)
            
            if order.side == OrderSide.SELL and tick.bid >= order.price:
                return self._create_trade(order,order.price)
            
            return None
        
        if order.order_type == OrderType.STOP_LOSS:
            if order.side == OrderSide.BUY and tick.ltp >= order.trigger_price:
                fill_price = tick.ask
                return self._create_trade(order,fill_price)
            
            if order.side == OrderSide.SELL and tick.ltp <= order.trigger_price:
                fill_price = tick.bid
                return self._create(order,fill_price)
            
            return None
        
        def _create_trade(self, order: Order, price: float) -> Trade:
            return Trade(
                trade_id = str(uuid4()),
                order_id = order.order_id,
                symbol = order.symbol,
                instrument_type = order.instrument_type,
                side = order.side,
                quantity = order.remaining_quantity,
                price = price,
                source = order.source 
            )
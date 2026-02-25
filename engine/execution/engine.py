from typing import Dict, List

from engine.core.order import Order
from engine.core.trade import Trade
from engine.core.position import Position
from engine.core.account import Account
from engine.core.enums import OrderStatus
from engine.execution.matcher import Matcher
from engine.market.tick import MarketTick

class ExecutionEngine:
    def __init__(self, account: Account):
        self.account = account
        self.matcher = Matcher()
        
        self.open_orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        
    def submit_order(self, order:Order):
        order.status = OrderStatus.OPEN
        self.open_orders[order.order_id] = order
        
    def on_tick(self, tick:MarketTick) -> List[Trade]:
        trades: List[Trade] = []
        
        for order_id, order in list(self.open_orders.items()):
            trade = self.matcher.match(order,tick)
            
            if trade:
                trades.append(trade)
                self._process_trade(order,trade)
                
        return trades
    
    def _process_trade(self,order:Order, trade:Trade):
        
        order.filled_quantity += trade.quantity
        
        if order.remaining_quantity() == 0:
            order.status = OrderStatus.FILLED
            self.open_orders.pop(order.order_id, None)
            
        position = self.positions.get(trade.symbol)
        
        if not position:
            position = Position(symbol=trade.symbol)
            self.positions[trade.symbol] = position
        
        previous_realized = position.realized_pnl
        
        position.apply_trade(trade)
        
        pnl_change = position.realized_pnl - previous_realized
        if pnl_change != 0:
            self.account.apply_realized_pnl(pnl_change)
        
        
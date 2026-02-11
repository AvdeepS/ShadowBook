from dataclasses import dataclass
from typing import Optional

from engine.core.trade import Trade
from engine.core.enums import OrderSide

@dataclass
class Position:
    symbol: str
    
    quantity: int = 0  #+ve for long, -ve for short
    average_price: float = 0.0 #weighted avg
    realized_pnl: float = 0.0 
    
    def apply_trade(self, trade: Trade):
        trade_qty = trade.quantity if trade.side == OrderSide.BUY else -trade.quantity #passes positive if buy otherwise negative to fulfill -ve for short criteria 
        
        #new position
        if self.quantity == 0:
            self.quantity = trade_qty
            self.average_price = trade.price
            return
        
        #increasing same direction positions
        if (self.quantity > 0 and trade_qty>0) or (self.quantity<0 and trade_qty<0):
            total_cost = (abs(self.quantity)*self.average_price) + (abs(trade_qty)*trade.price)
            new_qty = self.quantity + trade_qty
            
            self.average_price = total_cost/abs(new_qty)
            self.quantity = new_qty
            return
        
        #decreasing/reversing positions
        if abs(trade_qty) < abs(self.quantity):
            
            pnl = abs(trade_qty) * (self.average_price - trade.price)
            if self.quantity > 0:
                pnl *= -1 #loss if trade < avg price
                
            self.realized_pnl += pnl
            self.quantity += trade_qty
            return
        
        elif abs(trade_qty) == abs(self.quantity):
            #full square off
            pnl = abs(trade_qty) * (self.average_price - trade.price)
            if self.quantity >0:
                pnl *= -1
            
            self.realized_pnl += pnl
            self.quantity = 0
            self.average_price = 0.0
            return
        
        else:
            
            closing_qty = -self.quantity
            pnl = abs(closing_qty) * (self.average_price - trade.price)
            if self.quantity > 0:
                pnl *= -1
                
            self.realized_pnl += pnl
            
            remaining_qty = trade_qty + self.quantity
            self.quantity = remaining_qty
            self.average_price = trade.price
        
    def unrealized_pnl(self, current_price: float) -> float:
        if self.quantity == 0:
            return 0.0
        
        return self.quantity * (current_price - self.average_price)
            
             
        
        
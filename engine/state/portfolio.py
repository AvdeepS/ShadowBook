from dataclasses import dataclass
from typing import Dict
from engine.core.position import Position
from engine.core.account import Account

@dataclass
class Portfolio:
    
    account: Account
    positions: dict[str, Position]
    
    def total_unrealized_pnl(self, price_map: Dict[str,float]) -> float:
        total = 0.0
        
        for symbol, position in self.positions.items():
            if symbol in price_map:
                total += position.unrealized_pnl(price_map[symbol])
                
        return total

    def total_equity(self, price_map: Dict[str,float]) -> float:
        return(
            self.account.cash_balance +
            self.account.blocked_marhgin +
            self.total_unrealized_pnl(price_map)
        )
    
    def total_exposure(self, price_map: Dict[str,float]) -> float:
        exposure = 0.0
        
        for symbol, position in self.positions.items():
            if symbol in price_map:
                exposure += abs(position.quantity * price_map[symbol])
                
        return exposure
        
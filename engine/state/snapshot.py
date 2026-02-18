from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class PositionSnapshot:
    symbol: str
    quantity: float
    average_price: float
    unrealized_pnl: float
    realized_pnl: float
    
@dataclass(frozen=True)
class PortfolioSnapshot:
    timestamp: int
    
    cash_balance: float
    blocked_margin: float
    
    total_unrealized_pnl: float
    total_equity: float
    total_exposure: float
    
    positions: Dict[str,PositionSnapshot]
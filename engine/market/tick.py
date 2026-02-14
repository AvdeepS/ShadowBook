from dataclasses import dataclass
from datetime import datetime as dt

@dataclass(frozen=True)
class MarketTick:
    symbol: str
    
    bid: float
    ask: float
    ltp: float
    
    tiemstamp: dt
    
    def __post_init__(self):
        if self.bid <= 0 or self.ask <0 or self.ltp <= 0:
            raise ValueError("Prices must be positive")
        
        if self.bid > self.ask:
            raise ValueError("Bid cannot exceed ask")
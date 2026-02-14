from dataclasses import dataclass
from datetime import date
from typing import Optional

from engine.core.enums import InstrumentType, OptionType

@dataclass(frozen=True)
class Instrument:
    symbol:str
    instrument_type: InstrumentType
    
    lot_size: int
    tick_size: int
    
    expiry: Optional[date] = None
    strike: Optional[float] = None
    option_type: Optional[OptionType] = None

    def __post_init__(self):
        if self.lot_size <= 0:
            raise ValueError("Lot size must be positive")
        
        if self.tick_size <= 0:
            raise ValueError("Tick size must be positive")
        
        if self.instrument_type == InstrumentType.OPTION:
            if self.strike is None or self.option_type is None or self.expiry is None:
                raise ValueError("Option instruments require strike, option type and expiry")
        
        if self.instrument_type == InstrumentType.FUTURE:
            if self.expiry is None:
                raise ValueError("Future instruments require expiry")
from enum import Enum

class OrderSide(Enum): #trade directioN
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum): #execution intent
    MARKET = "MARKET"
    LIMIT = "LIMIT" 
    STOP_LOSS = "STOP_LOSS"
    
class OrderStatus(Enum): #order lifecycle state
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED" 
    REJECTED = "REJECTED"

class OrderValiditity(Enum): #time validity
    GTC = "GTC"
    
class InstrumentType(Enum): #asset classes
    EQUITY = "EQUITY"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    
class OptionType(Enum): #option payoff type
    CALL = "CALL"
    PUT = "PUT"
    
class PositionSide(Enum): #derived position direction
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"
    
class TradeSource(Enum): #origin of trade
    MANUAL = "MANUAL"
    ALGO = "ALGO"
    SYSTEM = "SYSTEM"  #includes automatic liquidiation, stop loss orders, F&O expiry etc.
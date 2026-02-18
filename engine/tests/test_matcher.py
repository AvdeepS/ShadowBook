from engine.execution.matcher import Matcher
from engine.core.order import Order
from engine.market.tick import MarketTick
from engine.core.enums import OrderSide, OrderType, InstrumentType, TradeSource

def test_limit_buy_order_fill():
    matcher = Matcher()
    
    order = Order(
        #trade_id = 1,
        order_id = 1,
        symbol = "RIL",
        instrument_type = InstrumentType.EQUITY,
        side = OrderSide.BUY,
        quantity = 100,
        price = 100,
        source = TradeSource.MANUAL,
        order_type=OrderType.LIMIT
    )
    
    tick = MarketTick(
        symbol="RIL",
        ltp = 99,
        tiemstamp= 1,
        bid = 97,
        ask = 99
    )
    
    trade = matcher.match(order,tick)
    
    assert trade is not None
    assert trade.price == 99
    
def test_limit_sell_order_fill():
    matcher = Matcher()
    
    order = Order(
        #trade_id = 1,
        order_id = 1,
        symbol = "RIL",
        instrument_type = InstrumentType.EQUITY,
        side = OrderSide.SELL,
        quantity = 100,
        price = 100,
        source = TradeSource.MANUAL,
        order_type=OrderType.LIMIT
    )
    
    tick = MarketTick(
        symbol="RIL",
        ltp = 99,
        tiemstamp= 1,
        bid = 101,
        ask = 103
    )
    
    trade = matcher.match(order,tick)
    
    assert trade is not None
    assert trade.price == 101
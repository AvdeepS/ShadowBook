from engine.core.position import Position
from engine.core.trade import Trade
from engine.core.enums import OrderSide

def test_open_long_position():
    position = Position(symbol="RIL")
    
    trade = Trade(
        source="SIM",
        instrument_type="EQUITY",
        trade_id="t1",
        order_id="o1",
        symbol="RIL",
        quantity=10,
        price=100,
        side = OrderSide.BUY
    )
    
    position.apply_trade(trade)
    
    assert position.quantity == 10
    assert position.average_price == 100
    assert position.realized_pnl == 0
    
def test_add_to_long():
    position = Position(symbol="RIL")
    
    trade1 = Trade(
        source="SIM",
        instrument_type="EQUITY",
        trade_id="t1",
        order_id="o1",
        symbol="RIL",
        quantity=10,
        price=100,
        side = OrderSide.BUY
    )
    
    trade2 = Trade(
        source="SIM",
        instrument_type="EQUITY",
        trade_id="t1",
        order_id="o1",
        symbol="RIL",
        quantity=10,
        price=110,
        side = OrderSide.BUY
    )
    
    position.apply_trade(trade1)
    position.apply_trade(trade2)
    
    assert position.quantity == 20
    assert position.average_price == 105
    
def test_partial_close_long():
    position = Position(symbol="RIL")
    
    trade1 = Trade(
        source="SIM",
        instrument_type="EQUITY",
        trade_id="t1",
        order_id="o1",
        symbol="RIL",
        quantity=10,
        price=100,
        side = OrderSide.BUY
    )
    
    trade2 = Trade(
        source="SIM",
        instrument_type="EQUITY",
        trade_id="t1",
        order_id="o1",
        symbol="RIL",
        quantity=5,
        price=110,
        side = OrderSide.SELL
    )
    
    position.apply_trade(trade1)
    position.apply_trade(trade2)
    
    assert position.quantity == 5
    assert position.realized_pnl == 50
    
def test_flip_position():
    position = Position(symbol="RIL")
    
    trade1 = Trade(
        source="SIM",
        instrument_type="EQUITY",
        trade_id="t1",
        order_id="o1",
        symbol="RIL",
        quantity=10,
        price=100,
        side = OrderSide.BUY
    )
    
    trade2 = Trade(
        source="SIM",
        instrument_type="EQUITY",
        trade_id="t1",
        order_id="o1",
        symbol="RIL",
        quantity=20,
        price=90,
        side = OrderSide.SELL
    )

    position.apply_trade(trade1)
    position.apply_trade(trade2)

    assert position.quantity == -10
    assert position.average_price == 90
    assert position.realized_pnl == -100  
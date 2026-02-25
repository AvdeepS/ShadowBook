from engine.execution.engine import ExecutionEngine
from engine.core.account import Account
from engine.core.order import Order
from engine.core.enums import TradeSource,InstrumentType,OrderType, OrderSide
from engine.market.tick import MarketTick
from engine.state.portfolio import Portfolio

def test_full_execution():
    
    account = Account(initial_capital=1000000)
    engine = ExecutionEngine(account)
    
    buy_order = Order(
        order_id="o1",
        symbol= "RIL",
        instrument_type=InstrumentType.EQUITY,
        side=OrderSide.BUY,
        quantity=10,
        order_type=OrderType.MARKET,
        price=None,
        trigger_price=None,
        source=TradeSource.MANUAL
    )
    
    engine.submit_order(buy_order)
    
    tick=MarketTick(
        symbol="RIL",
        bid=99,
        ask=100,
        ltp=100,
        timestamp=1
    )
    
    trades = engine.on_tick(tick)
    
    assert len(trades) ==1
    assert buy_order.is_open() is False
    
    position = engine.positions["RIL"]
    
    assert position.quantity == 10
    assert position.average_price == 100
    assert position.realized_pnl == 0
    
    portfolio = Portfolio(account=account, positions = engine.positions)
    
    price_map = {"RIL":110}
    
    unrealized = portfolio.total_unrealized_pnl(price_map)
    assert unrealized == 100
    
    equity=portfolio.total_equity(price_map)
    assert equity == 1000000 + 100
    
    sell_order = Order(
        order_id="o2",
        symbol="RIL",
        instrument_type=InstrumentType.EQUITY,
        side=OrderSide.SELL,
        quantity=10,
        order_type=OrderType.MARKET,
        price=None,
        trigger_price=None,
        source=TradeSource.MANUAL
    )

    engine.submit_order(sell_order)

    tick2 = MarketTick(
        symbol="RIL",
        bid=110,
        ask=111,
        ltp=110,
        timestamp=2
    )

    trades2 = engine.on_tick(tick2)

    assert len(trades2) == 1

    # Position should now be flat
    position = engine.positions["RIL"]
    assert position.quantity == 0

    # Realized pnl should be applied
    assert position.realized_pnl == 100

    # Account should reflect realized pnl
    assert account.cash_balance == 1000000 + 100

    # Final equity should equal cash
    final_equity = portfolio.total_equity({"RIL": 110})
    assert final_equity == 1000100
    

    
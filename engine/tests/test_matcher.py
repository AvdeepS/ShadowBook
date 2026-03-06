import pytest

from engine.core.enums import (
    InstrumentType,
    OrderSide,
    OrderStatus,
    OrderType,
    TradeSource,
)
from engine.core.order import Order
from engine.execution.matcher import Matcher
from engine.market.tick import MarketTick


def make_order(**overrides): #overrides is a dictionary which accepts any number of kwargs
    payload = {
        "order_id": "o1",
        "symbol": "RIL",
        "instrument_type": InstrumentType.EQUITY,
        "side": OrderSide.BUY,
        "order_type": OrderType.LIMIT,
        "quantity": 100,
        "price": 100,
        "source": TradeSource.MANUAL,
    }
    payload.update(overrides)
    return Order(**payload)


def make_tick(**overrides):
    payload = {
        "symbol": "RIL",
        "bid": 99,
        "ask": 100,
        "ltp": 100,
        "timestamp": 1,
    }
    payload.update(overrides)
    return MarketTick(**payload)


def test_returns_none_for_symbol_mismatch():
    matcher = Matcher()
    order = make_order(symbol="INFY")
    tick = make_tick(symbol="RIL")

    assert matcher.match(order, tick) is None


def test_returns_none_for_closed_order():
    matcher = Matcher()
    order = make_order(status=OrderStatus.CANCELLED)
    tick = make_tick()

    assert matcher.match(order, tick) is None


@pytest.mark.parametrize( #allows for different values to be input into the same test
    "side,bid,ask,expected_price",
    [
        (OrderSide.BUY, 99, 101, 101),
        (OrderSide.SELL, 99, 101, 99),
    ],
)
def test_market_order_fills_using_best_quote(side, bid, ask, expected_price):
    matcher = Matcher()
    order = make_order(order_type=OrderType.MARKET, side=side, price=None)
    tick = make_tick(bid=bid, ask=ask)

    trade = matcher.match(order, tick)

    assert trade is not None
    assert trade.price == expected_price


def test_limit_buy_order_fills_when_ask_at_or_below_limit():
    matcher = Matcher()
    order = make_order(side=OrderSide.BUY, price=100)
    tick = make_tick(ask=99)

    trade = matcher.match(order, tick)

    assert trade is not None
    assert trade.price == 99


def test_limit_sell_order_fills_when_bid_at_or_above_limit():
    matcher = Matcher()
    order = make_order(side=OrderSide.SELL, price=100)
    tick = make_tick(bid=101, ask=102)

    trade = matcher.match(order, tick)

    assert trade is not None
    assert trade.price == 101


@pytest.mark.parametrize(
    "side,bid,ask,limit_price",
    [
        (OrderSide.BUY, 98, 101, 100),
        (OrderSide.SELL, 99, 102, 100),
    ],
)
def test_limit_order_does_not_fill_when_price_conditions_not_met(side, bid, ask, limit_price):
    matcher = Matcher()
    order = make_order(side=side, price=limit_price)
    tick = make_tick(bid=bid, ask=ask)

    assert matcher.match(order, tick) is None


@pytest.mark.parametrize(
    "side,ltp,trigger_price,bid,ask,expected_price",
    [
        (OrderSide.BUY, 106, 105, 104, 106, 106),
        (OrderSide.SELL, 94, 95, 94, 96, 94),
    ],
)
def test_stop_loss_order_fills_when_trigger_hit(
    side, ltp, trigger_price, bid, ask, expected_price
):
    matcher = Matcher()
    order = make_order(
        side=side,
        order_type=OrderType.STOP_LOSS,
        price=None,
        trigger_price=trigger_price,
    )
    tick = make_tick(ltp=ltp, bid=bid, ask=ask)

    trade = matcher.match(order, tick)

    assert trade is not None
    assert trade.price == expected_price


@pytest.mark.parametrize(
    "side,ltp,trigger_price",
    [
        (OrderSide.BUY, 104, 105),
        (OrderSide.SELL, 96, 95),
    ],
)
def test_stop_loss_order_does_not_fill_when_trigger_not_hit(side, ltp, trigger_price):
    matcher = Matcher()
    order = make_order(
        side=side,
        order_type=OrderType.STOP_LOSS,
        price=None,
        trigger_price=trigger_price,
    )
    tick = make_tick(ltp=ltp)

    assert matcher.match(order, tick) is None


def test_trade_quantity_uses_remaining_order_quantity():
    matcher = Matcher()
    order = make_order(order_type=OrderType.MARKET, quantity=100, filled_quantity=35, price=None)
    tick = make_tick(bid=98, ask=99)

    trade = matcher.match(order, tick)

    assert trade is not None
    assert trade.quantity == 65
import pytest

from engine.core.enums import InstrumentType, OrderSide, TradeSource
from engine.core.position import Position
from engine.core.trade import Trade


def make_trade(side, quantity, price, symbol="RIL", trade_id="t1"):
    return Trade(
        source=TradeSource.SYSTEM,
        instrument_type=InstrumentType.EQUITY,
        trade_id=trade_id,
        order_id=f"o-{trade_id}",
        symbol=symbol,
        quantity=quantity,
        price=price,
        side=side,
    )


def test_open_long_position():
    position = Position(symbol="RIL")
    position.apply_trade(make_trade(OrderSide.BUY, 10, 100))

    assert position.quantity == 10
    assert position.average_price == 100
    assert position.realized_pnl == 0


def test_add_to_long_recomputes_weighted_average():
    position = Position(symbol="RIL")

    position.apply_trade(make_trade(OrderSide.BUY, 10, 100, trade_id="t1"))
    position.apply_trade(make_trade(OrderSide.BUY, 10, 110, trade_id="t2"))

    assert position.quantity == 20
    assert position.average_price == 105


def test_partial_close_long_realizes_profit():
    position = Position(symbol="RIL")

    position.apply_trade(make_trade(OrderSide.BUY, 10, 100, trade_id="t1"))
    position.apply_trade(make_trade(OrderSide.SELL, 5, 110, trade_id="t2"))

    assert position.quantity == 5
    assert position.average_price == 100
    assert position.realized_pnl == 50


def test_full_close_long_resets_position_state():
    position = Position(symbol="RIL")

    position.apply_trade(make_trade(OrderSide.BUY, 10, 100, trade_id="t1"))
    position.apply_trade(make_trade(OrderSide.SELL, 10, 90, trade_id="t2"))

    assert position.quantity == 0
    assert position.average_price == 0.0
    assert position.realized_pnl == -100


def test_flip_from_long_to_short_updates_average_to_new_trade_price():
    position = Position(symbol="RIL")

    position.apply_trade(make_trade(OrderSide.BUY, 10, 100, trade_id="t1"))
    position.apply_trade(make_trade(OrderSide.SELL, 20, 90, trade_id="t2"))

    assert position.quantity == -10
    assert position.average_price == 90
    assert position.realized_pnl == -100


def test_open_short_position_and_add_to_short():
    position = Position(symbol="RIL")

    position.apply_trade(make_trade(OrderSide.SELL, 10, 120, trade_id="t1"))
    position.apply_trade(make_trade(OrderSide.SELL, 10, 100, trade_id="t2"))

    assert position.quantity == -20
    assert position.average_price == 110


def test_partial_cover_short_realizes_profit():
    position = Position(symbol="RIL")

    position.apply_trade(make_trade(OrderSide.SELL, 10, 120, trade_id="t1"))
    position.apply_trade(make_trade(OrderSide.BUY, 4, 100, trade_id="t2"))

    assert position.quantity == -6
    assert position.average_price == 120
    assert position.realized_pnl == 80


def test_flip_from_short_to_long_realizes_pnl_and_sets_new_average():
    position = Position(symbol="RIL")

    position.apply_trade(make_trade(OrderSide.SELL, 10, 120, trade_id="t1"))
    position.apply_trade(make_trade(OrderSide.BUY, 15, 130, trade_id="t2"))

    assert position.quantity == 5
    assert position.average_price == 130
    assert position.realized_pnl == -100


@pytest.mark.parametrize(
    "starting_trade,market_price,expected",
    [
        (make_trade(OrderSide.BUY, 10, 100), 110, 100),
        (make_trade(OrderSide.SELL, 10, 100), 90, 100),
    ],
)
def test_unrealized_pnl_for_long_and_short(starting_trade, market_price, expected):
    position = Position(symbol="RIL")
    position.apply_trade(starting_trade)

    assert position.unrealized_pnl(market_price) == expected


def test_unrealized_pnl_is_zero_for_flat_position():
    position = Position(symbol="RIL")

    assert position.unrealized_pnl(123) == 0.0

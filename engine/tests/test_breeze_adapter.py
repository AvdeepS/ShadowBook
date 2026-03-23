from datetime import datetime as dt

import pytest

from engine.integrations.breeze_adapter import BreezeAdapter, BreezeSubscription
from engine.utils.time import IST

class DummyBreezeClient:
    def __init__(self):
        self.connected = False
        self.subscriptions = []
        
    def ws_connect(self): #mock ws connection
        self.connected = True
    
def test_connect_calls_ws_connect():
    client = DummyBreezeClient()
    adapter = BreezeAdapter(client)
    
    adapter.connect()
    
    assert client.connected is True


def test_subscribe_forwards_subscription_payloads():
    client = DummyBreezeClient()
    adapter = BreezeAdapter(client)
    
    adapter.subscribe(
        [
            BreezeSubscription(stock_token="NIFTY"),
            BreezeSubscription(stock_token="RELIANCE", exchange_code="NFO", product_type="futures")
            
        ]
    )
    
    assert len(client.subscriptions) == 2
    assert client.subscriptions[0]["stock_token"] == "NIFTY"
    assert client.subscriptions[1]["exchange_code"] == "NFO"
    

def test_normalize_tick_maps_typical_breeze_payload():
    adapter = BreezeAdapter(DummyBreezeClient())

    tick = adapter.normalize_tick(
        {
            "stock_code": "RELIANCE",
            "best_bid_price": 2450.25,
            "best_offer_price": 2450.75,
            "last_traded_price": 2450.60,
            "ltt": "2024-12-01T09:15:00+05:30",
        }
    )

    assert tick.symbol == "RELIANCE"
    assert tick.bid == pytest.approx(2450.25)
    assert tick.ask == pytest.approx(2450.75)
    assert tick.ltp == pytest.approx(2450.60)
    assert tick.tiemstamp.tzinfo == IST
    
    
from __future__ import annotations

from dataclasses import dataclass

from app.broker import BrokerClient
from app.market import MarketAnalyzer, MarketDataFeed
from app.models import ConnectionRequest, ConnectionResponse, Order, OrderRequest


@dataclass
class TradingEngine:
    broker: BrokerClient
    market_feed: MarketDataFeed
    analyzer: MarketAnalyzer

    def connect(self, payload: ConnectionRequest) -> ConnectionResponse:
        session = self.broker.connect(str(payload.gmail), payload.senha)
        return ConnectionResponse(status=session.status, connected_at=session.connected_at)

    def disconnect(self) -> ConnectionResponse:
        session = self.broker.disconnect()
        return ConnectionResponse(status=session.status, connected_at=session.connected_at)

    def analyze_market(self, symbol: str):
        candles = self.market_feed.get_candles(symbol=symbol, limit=30)
        return self.analyzer.snapshot(symbol=symbol.upper(), candles=candles)

    def place_order(self, payload: OrderRequest) -> Order:
        snapshot = self.analyze_market(payload.symbol)

        if snapshot.signal == "wait":
            order = self.broker.place_order(payload)
            order.reason = "mercado lateral; ordem pendente aguardando confirmação"
            return order

        order = self.broker.place_order(payload)
        return self.broker.refresh_order(order.id, snapshot.signal, payload.expiration_seconds)

    def refresh_order(self, order_id: str, symbol: str, expiration_seconds: int = 60) -> Order:
        snapshot = self.analyze_market(symbol)
        return self.broker.refresh_order(order_id=order_id, trend_signal=snapshot.signal, expiration_seconds=expiration_seconds)

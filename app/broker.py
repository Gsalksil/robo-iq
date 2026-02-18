from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict

from app.models import ConnectionStatus, Order, OrderRequest, OrderStatus, new_order_id


@dataclass
class BrokerSession:
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    gmail: str | None = None
    connected_at: datetime | None = None


class BrokerClient:
    """Cliente de corretora simulado para rodar localmente via API."""

    def __init__(self):
        self.session = BrokerSession()
        self._orders: Dict[str, Order] = {}

    def connect(self, gmail: str, senha: str) -> BrokerSession:
        if not gmail.endswith("@gmail.com"):
            raise ValueError("apenas conta gmail é suportada")
        if len(senha.strip()) < 8:
            raise ValueError("senha inválida")

        self.session = BrokerSession(
            status=ConnectionStatus.CONNECTED,
            gmail=gmail,
            connected_at=datetime.now(timezone.utc),
        )
        return self.session

    def disconnect(self) -> BrokerSession:
        self.session.status = ConnectionStatus.DISCONNECTED
        return self.session

    def ensure_connected(self):
        if self.session.status != ConnectionStatus.CONNECTED:
            raise RuntimeError("robô desconectado da plataforma")

    def place_order(self, payload: OrderRequest) -> Order:
        self.ensure_connected()
        now = datetime.now(timezone.utc)
        order = Order(
            id=new_order_id(),
            symbol=payload.symbol.upper(),
            side=payload.side,
            amount=payload.amount,
            status=OrderStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._orders[order.id] = order
        return order

    def cancel_order(self, order_id: str) -> Order:
        self.ensure_connected()
        if order_id not in self._orders:
            raise KeyError("ordem não encontrada")

        order = self._orders[order_id]
        if order.status in {OrderStatus.EXECUTED, OrderStatus.CANCELED, OrderStatus.REJECTED}:
            return order

        order.status = OrderStatus.CANCELED
        order.updated_at = datetime.now(timezone.utc)
        self._orders[order_id] = order
        return order

    def refresh_order(self, order_id: str, trend_signal: str, expiration_seconds: int) -> Order:
        if order_id not in self._orders:
            raise KeyError("ordem não encontrada")

        order = self._orders[order_id]
        if order.status != OrderStatus.PENDING:
            return order

        elapsed = datetime.now(timezone.utc) - order.created_at
        expiration = timedelta(seconds=expiration_seconds)

        if elapsed > expiration:
            order.status = OrderStatus.CANCELED
            order.reason = "ordem expirada"
        elif (order.side.value == "buy" and trend_signal == "buy") or (
            order.side.value == "sell" and trend_signal == "sell"
        ):
            order.status = OrderStatus.EXECUTED
            order.reason = "executada por alinhamento com sinal de mercado"

        order.updated_at = datetime.now(timezone.utc)
        self._orders[order_id] = order
        return order

    def get_order(self, order_id: str) -> Order:
        if order_id not in self._orders:
            raise KeyError("ordem não encontrada")
        return self._orders[order_id]

    def list_orders(self) -> list[Order]:
        return sorted(self._orders.values(), key=lambda o: o.created_at, reverse=True)

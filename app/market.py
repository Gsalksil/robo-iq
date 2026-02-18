from __future__ import annotations

from datetime import datetime, timedelta, timezone
from random import Random

from app.models import Candle, MarketSnapshot, MarketTrend


class MarketDataFeed:
    """Gera candles sintéticos determinísticos por símbolo para simulação local."""

    def __init__(self, seed: int = 42):
        self._rng = Random(seed)

    def get_candles(self, symbol: str, limit: int = 30) -> list[Candle]:
        now = datetime.now(timezone.utc)
        base_price = 100 + (sum(ord(c) for c in symbol) % 30)
        candles: list[Candle] = []
        previous_close = float(base_price)

        for idx in range(limit):
            ts = now - timedelta(minutes=limit - idx)
            noise = self._rng.uniform(-1.2, 1.2)
            drift = (idx / max(limit, 1)) * self._rng.uniform(-0.4, 0.4)
            open_price = previous_close
            close_price = max(1.0, open_price + noise + drift)
            high_price = max(open_price, close_price) + self._rng.uniform(0.05, 0.7)
            low_price = min(open_price, close_price) - self._rng.uniform(0.05, 0.7)
            low_price = max(0.1, low_price)

            candles.append(
                Candle(
                    timestamp=ts,
                    open=round(open_price, 5),
                    high=round(high_price, 5),
                    low=round(low_price, 5),
                    close=round(close_price, 5),
                    volume=round(self._rng.uniform(50, 1000), 2),
                )
            )
            previous_close = close_price

        return candles


class MarketAnalyzer:
    def __init__(self, fast_period: int = 5, slow_period: int = 20):
        if fast_period >= slow_period:
            raise ValueError("fast_period deve ser menor que slow_period")
        self.fast_period = fast_period
        self.slow_period = slow_period

    def snapshot(self, symbol: str, candles: list[Candle]) -> MarketSnapshot:
        if len(candles) < self.slow_period:
            raise ValueError("quantidade de candles insuficiente para análise")

        closes = [c.close for c in candles]
        fast_ma = sum(closes[-self.fast_period :]) / self.fast_period
        slow_ma = sum(closes[-self.slow_period :]) / self.slow_period
        current_price = closes[-1]

        if fast_ma > slow_ma * 1.002:
            trend = MarketTrend.BULLISH
            signal = "buy"
        elif fast_ma < slow_ma * 0.998:
            trend = MarketTrend.BEARISH
            signal = "sell"
        else:
            trend = MarketTrend.SIDEWAYS
            signal = "wait"

        return MarketSnapshot(
            symbol=symbol,
            current_price=round(current_price, 5),
            moving_average_fast=round(fast_ma, 5),
            moving_average_slow=round(slow_ma, 5),
            trend=trend,
            signal=signal,
            candles=candles,
        )

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.broker import BrokerClient
from app.market import MarketAnalyzer, MarketDataFeed
from app.models import ConnectionRequest, ConnectionResponse, HealthResponse, OrderActionResponse, OrderRequest
from app.services import TradingEngine


app = FastAPI(title="Robo IQ API", version="0.1.0")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")

engine = TradingEngine(broker=BrokerClient(), market_feed=MarketDataFeed(seed=42), analyzer=MarketAnalyzer())


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.post("/connect", response_model=ConnectionResponse)
def connect(payload: ConnectionRequest) -> ConnectionResponse:
    try:
        return engine.connect(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/disconnect", response_model=ConnectionResponse)
def disconnect() -> ConnectionResponse:
    return engine.disconnect()


@app.get("/market/{symbol}")
def market_snapshot(symbol: str):
    try:
        return engine.analyze_market(symbol)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/orders", response_model=OrderActionResponse)
def create_order(payload: OrderRequest) -> OrderActionResponse:
    try:
        order = engine.place_order(payload)
        return OrderActionResponse(order=order)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/orders")
def list_orders():
    return engine.broker.list_orders()


@app.get("/orders/{order_id}", response_model=OrderActionResponse)
def get_order(order_id: str) -> OrderActionResponse:
    try:
        return OrderActionResponse(order=engine.broker.get_order(order_id))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/orders/{order_id}/monitor", response_model=OrderActionResponse)
def monitor_order(order_id: str) -> OrderActionResponse:
    try:
        order = engine.broker.get_order(order_id)
        updated = engine.refresh_order(order_id=order_id, symbol=order.symbol, expiration_seconds=60)
        return OrderActionResponse(order=updated)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/orders/{order_id}/cancel", response_model=OrderActionResponse)
def cancel_order(order_id: str) -> OrderActionResponse:
    try:
        return OrderActionResponse(order=engine.broker.cancel_order(order_id))
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

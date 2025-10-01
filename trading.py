
import numpy as np
import pandas as pd

BROKER_READY = False
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    BROKER_READY = True
except Exception:
    BROKER_READY = False

def suggest_orders(last_px: pd.Series, weights: pd.Series, equity: float) -> pd.DataFrame:
    out = []
    for sym, w in weights.items():
        px = float(last_px.get(sym, np.nan))
        if not np.isfinite(px): 
            continue
        dollars = w * equity
        qty = int(np.floor(abs(dollars)/px))
        if qty <= 0: 
            continue
        side = "buy" if dollars > 0 else "sell"
        out.append(dict(symbol=sym, side=side, qty=qty, price=round(px,2), weight=round(w,4), notional=round(qty*px,2)))
    return pd.DataFrame(out).sort_values(["side","symbol"]).reset_index(drop=True)

def cap_weights(w: pd.Series, per_cap: float, gross_cap: float) -> pd.Series:
    w = w.clip(-per_cap, per_cap)
    gross = w.abs().sum()
    if gross > gross_cap and gross > 0:
        w = w * (gross_cap / gross)
    return w

def alpaca_submit_orders(orders_df: pd.DataFrame, key: str, secret: str, paper=True):
    if not BROKER_READY:
        return False, "alpaca-py not installed in environment."
    if orders_df.empty:
        return False, "No orders to submit."
    try:
        client = TradingClient(api_key=key, secret_key=secret, paper=paper)
        for _, row in orders_df.iterrows():
            req = MarketOrderRequest(
                symbol=row["symbol"],
                qty=int(row["qty"]),
                side=OrderSide.BUY if row["side"].lower()=="buy" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY,
            )
            client.submit_order(req)
        return True, f"Submitted {len(orders_df)} market orders."
    except Exception as e:
        return False, str(e)

def risk_checks_ok(daily_loss_limit_pct: float) -> bool:
    # Placeholder (needs broker PnL to enforce)
    return True

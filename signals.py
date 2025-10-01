
import numpy as np
import pandas as pd

def strategy_list():
    return ["SMA crossover (50/200)", "RSI mean reversion", "MACD", "Momentum (12-1)"]

def sma_crossover(px: pd.Series, fast=50, slow=200):
    sma_f = px.rolling(fast).mean()
    sma_s = px.rolling(slow).mean()
    sig = (sma_f > sma_s).astype(int)
    aux = pd.DataFrame({"Price": px, f"SMA{fast}": sma_f, f"SMA{slow}": sma_s})
    return sig, aux

def rsi(px: pd.Series, n=14):
    chg = px.diff()
    up = chg.clip(lower=0).rolling(n).mean()
    dn = -chg.clip(upper=0).rolling(n).mean()
    rs = up / (dn + 1e-12)
    return 100 - 100/(1+rs)

def rsi_mean_rev(px: pd.Series, n=14, buy_below=30, sell_above=70):
    r = rsi(px, n)
    sig = pd.Series(0, index=px.index)
    sig[r < buy_below] = 1
    sig[r > sell_above] = 0
    sig = sig.ffill().astype(int)
    aux = pd.DataFrame({"Price": px, f"RSI{n}": r})
    return sig, aux

def macd(px: pd.Series, fast=12, slow=26, signal=9):
    ema_f = px.ewm(span=fast, adjust=False).mean()
    ema_s = px.ewm(span=slow, adjust=False).mean()
    macd = ema_f - ema_s
    sigl = macd.ewm(span=signal, adjust=False).mean()
    sig = (macd > sigl).astype(int)
    aux = pd.DataFrame({"Price": px, "MACD": macd, "Signal": sigl})
    return sig, aux

def momentum_12m(px: pd.Series, lkb=252, skip=21):
    ret = px.pct_change(lkb)
    ret = ret.shift(skip)
    sig = (ret > 0).astype(int)
    aux = pd.DataFrame({"Price": px, "12mRet": ret})
    return sig, aux

def build_signal(name: str, px: pd.Series):
    if name.startswith("SMA"):
        return sma_crossover(px)
    if name.startswith("RSI"):
        return rsi_mean_rev(px)
    if name.startswith("MACD"):
        return macd(px)
    if name.startswith("Momentum"):
        return momentum_12m(px)
    return sma_crossover(px)

def cross_sectional_mr(prices: pd.DataFrame, lookback=20, top_frac=0.2, cap=0.05):
    rets = prices.pct_change().fillna(0.0)
    demean = rets.sub(rets.mean(axis=1), axis=0)
    z = (demean - demean.rolling(lookback).mean())/(demean.rolling(lookback).std()+1e-8)
    alpha = -z.shift(1).iloc[-1].dropna()
    k = max(2, int(len(alpha)*top_frac))
    sel = alpha.abs().nlargest(k).index
    s = alpha[sel]
    if s.abs().sum() > 0:
        w = s / s.abs().sum()
    else:
        w = s * 0.0
    w = w.clip(-cap, cap)
    if w.abs().sum() > 0:
        w = w / w.abs().sum()
    return w

def apply_vol_target(returns: pd.Series, target_vol=0.10, lb=63, ann=252):
    vol = returns.rolling(lb).std()*np.sqrt(ann)
    scale = (target_vol / (vol.replace(0, np.nan))).fillna(0.0)
    return (returns * scale).fillna(0.0)

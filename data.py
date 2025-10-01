
from datetime import datetime
import pandas as pd
import yfinance as yf

try:
    import feedparser
    HAS_FEED = True
except Exception:
    HAS_FEED = False

def fetch_prices(symbols, start="2018-01-01", end=None):
    if not symbols:
        return pd.DataFrame()
    data = yf.download(symbols, start=start, end=end, progress=False, auto_adjust=False, group_by="column", threads=True)
    if isinstance(symbols, list) and len(symbols) == 1:
        if "Adj Close" in data:
            adj = data["Adj Close"].to_frame(symbols[0])
        elif "Close" in data:
            adj = data["Close"].to_frame(symbols[0])
        else:
            return pd.DataFrame()
    else:
        try:
            adj = data["Adj Close"]
        except Exception:
            adj = data["Close"] if "Close" in data else pd.DataFrame()
    adj = adj.dropna(how="all").sort_index()
    if adj.empty:
        return adj
    thresh = max(1, int(0.85*len(adj)))
    adj = adj.dropna(axis=1, thresh=thresh).ffill().bfill()
    return adj.apply(pd.to_numeric, errors="coerce")

def fetch_yf_news(ticker):
    out = []
    try:
        t = yf.Ticker(ticker)
        items = t.news or []
        for it in items:
            title = it.get("title","news")
            link = it.get("link","")
            pub = it.get("publisher","")
            ts = it.get("providerPublishTime", None)
            if isinstance(ts, (int, float)):
                ts = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M UTC")
            out.append(dict(title=title, link=link, publisher=pub, time=ts))
    except Exception:
        pass
    return out

def fetch_rss_feed(url):
    if not HAS_FEED:
        return ("RSS", [])
    try:
        feed = feedparser.parse(url)
        title = feed.feed.get("title","rss")
        entries = []
        for e in feed.entries:
            entries.append(dict(title=e.get("title","item"), link=e.get("link","")))
        return (title, entries)
    except Exception:
        return ("RSS", [])

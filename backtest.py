
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def backtest_portfolio(daily_returns: pd.Series, ann=252):
    daily_returns = daily_returns.fillna(0.0)
    equity = (1 + daily_returns).cumprod()
    if len(equity)==0:
        return equity, {}
    cagr = equity.iloc[-1]**(ann/len(equity)) - 1
    vol = np.sqrt(ann)*daily_returns.std()
    sharpe = (np.sqrt(ann)*daily_returns.mean() / (daily_returns.std()+1e-12)) if daily_returns.std()>0 else 0.0
    mdd = (1 - equity/equity.cummax()).max()
    stats = {"CAGR %": 100*cagr, "Vol %": 100*vol, "Sharpe": sharpe, "Max DD %": 100*mdd}
    return equity, stats

def perf_table(stats: dict) -> pd.DataFrame:
    if not stats: return pd.DataFrame({"Metric":[],"Value":[]})
    return pd.DataFrame({"Metric": list(stats.keys()), "Value": [round(v,3) if isinstance(v,(int,float)) else v for v in stats.values()]})

def rolling_stats_fig(equity: pd.Series, daily_returns: pd.Series, ann=252):
    if equity.empty:
        return go.Figure()
    roll_sharpe = np.sqrt(ann)*daily_returns.rolling(63).mean()/(daily_returns.rolling(63).std()+1e-12)
    drawdown = 1 - equity/equity.cummax()
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.5,0.25,0.25])
    fig.add_trace(go.Scatter(x=equity.index, y=equity.values, name="Equity"), row=1, col=1)
    fig.add_trace(go.Scatter(x=roll_sharpe.index, y=roll_sharpe.values, name="Rolling Sharpe"), row=2, col=1)
    fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown.values, name="Drawdown"), row=3, col=1)
    fig.update_layout(height=700, showlegend=True, margin=dict(l=10,r=10,t=30,b=10))
    return fig

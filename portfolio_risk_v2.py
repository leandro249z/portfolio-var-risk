"""
Portfolio risk: volatility, risk contribution, and Value-at-Risk (VaR) for a small stock portfolio.

Methods
  1. Historical VaR   - loss percentile of past portfolio returns (in-sample)
  2. Parametric VaR   - normal distribution: VaR = -(mu + z * sigma)
  3. Monte Carlo VaR  - simulated returns from historical mean and covariance
  4. Expected Shortfall (ES) - average loss beyond VaR
  5. Out-of-sample backtest - rolling 1-year window, Kupiec likelihood-ratio test
  6. Risk contribution - how much of portfolio volatility each holding causes

Usage
  python portfolio_risk_v2.py                    # Yahoo Finance prices (needs: pip install yfinance)
  python portfolio_risk_v2.py --csv prices.csv   # CSV: Date column + one adjusted-close column per ticker
  python portfolio_risk_v2.py --demo             # SIMULATED prices, only to test that the code runs

Outputs: printed summary, results.json, var_chart.png
"""
import argparse, json
import numpy as np
import pandas as pd
from scipy.stats import norm, chi2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TICKERS = ["LMT", "HON", "SPY", "JPM", "MSFT"]      # EDIT: your own portfolio
WEIGHTS = [0.25, 0.20, 0.25, 0.15, 0.15]            # EDIT: must sum to 1 (held constant; no rebalancing)
PORTFOLIO_VALUE = 100_000                           # EDIT: dollars
CONFIDENCE = 0.95
HORIZON_DAYS = 1
TRADING_DAYS = 252
ROLLING_WINDOW = 252                                # 1 trading year of history for each out-of-sample VaR
N_SIM = 100_000
SEED = 42


def load_prices(args):
    if args.demo:
        rng = np.random.default_rng(SEED)
        idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=1008)
        vols = np.array([0.20, 0.22, 0.16, 0.25, 0.28]) / np.sqrt(TRADING_DAYS)
        rets = rng.standard_t(5, (len(idx), len(TICKERS))) / np.sqrt(5 / 3) * vols
        return pd.DataFrame(100 * np.exp(rets.cumsum(0)), index=idx, columns=TICKERS)
    if args.csv:
        return pd.read_csv(args.csv, index_col=0, parse_dates=True)[TICKERS].dropna()
    import yfinance as yf
    px = yf.download(TICKERS, period="4y", auto_adjust=True, progress=False)["Close"]
    return px[TICKERS].dropna()


def kupiec_pvalue(breaches, n, alpha):
    """Kupiec proportion-of-failures test: is the breach rate consistent with alpha?"""
    x = breaches
    if x == 0:
        ll_null = (n) * np.log(1 - alpha)
        ll_alt = n * np.log(1.0)
    else:
        p_hat = x / n
        ll_null = (n - x) * np.log(1 - alpha) + x * np.log(alpha)
        ll_alt = (n - x) * np.log(1 - p_hat) + x * np.log(p_hat)
    lr = -2 * (ll_null - ll_alt)
    return float(lr), float(1 - chi2.cdf(lr, df=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv"); ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    w = np.array(WEIGHTS)
    assert abs(w.sum() - 1) < 1e-9, "weights must sum to 1"
    a = 1 - CONFIDENCE

    prices = load_prices(args)
    rets = np.log(prices / prices.shift(1)).dropna()
    port = rets.values @ w
    port = pd.Series(port, index=rets.index)
    res = {"start": str(prices.index[0].date()), "end": str(prices.index[-1].date()),
           "n_returns": int(len(rets)), "demo": bool(args.demo)}
    print(f"Data: {res['start']} to {res['end']} ({res['n_returns']} daily returns)")
    if args.demo:
        print("*** DEMO MODE: simulated prices. These numbers are NOT real market results. ***")

    # Volatility and risk contribution
    vol = rets.std() * np.sqrt(TRADING_DAYS)
    cov = rets.cov().values * TRADING_DAYS
    port_vol = float(np.sqrt(w @ cov @ w))
    marginal = cov @ w / port_vol
    contrib_pct = w * marginal / port_vol           # sums to 1
    res["annual_vol"] = {t: float(vol[t]) for t in TICKERS}
    res["portfolio_vol"] = port_vol
    res["risk_contribution"] = {t: float(c) for t, c in zip(TICKERS, contrib_pct)}
    print("\nAnnualized volatility and share of portfolio risk")
    for t, c in zip(TICKERS, contrib_pct):
        print(f"  {t:5s} vol {vol[t]:6.1%}   contributes {c:6.1%} of portfolio risk")
    print(f"  Portfolio vol {port_vol:6.1%}  (weighted-average vol {float(w @ vol.values):.1%}; gap = diversification)")
    print("\nCorrelation matrix\n", rets.corr().round(2))

    # In-sample VaR
    mu, sd = port.mean(), port.std()
    hist = -np.percentile(port, a * 100) * np.sqrt(HORIZON_DAYS)
    param = -(mu * HORIZON_DAYS + norm.ppf(a) * sd * np.sqrt(HORIZON_DAYS))
    rng = np.random.default_rng(SEED)
    sim = rng.multivariate_normal(rets.mean().values, rets.cov().values, N_SIM) @ w
    mc = -np.percentile(sim, a * 100) * np.sqrt(HORIZON_DAYS)
    es = -port[port <= np.percentile(port, a * 100)].mean() * np.sqrt(HORIZON_DAYS)
    res["var"] = {"historical": hist, "parametric": param, "monte_carlo": mc, "expected_shortfall": es}
    print(f"\n{HORIZON_DAYS}-day VaR at {CONFIDENCE:.0%} on ${PORTFOLIO_VALUE:,.0f} (full-sample)")
    for name, v in [("Historical", hist), ("Parametric (normal)", param), ("Monte Carlo", mc), ("Expected Shortfall", es)]:
        print(f"  {name:20s} {v:6.2%}  = ${v*PORTFOLIO_VALUE:,.0f}")

    # Out-of-sample rolling backtest (no look-ahead)
    var_fc, actual = [], []
    for t in range(ROLLING_WINDOW, len(port)):
        window = port.iloc[t - ROLLING_WINDOW:t]
        var_fc.append(-np.percentile(window, a * 100))
        actual.append(port.iloc[t])
    var_fc = pd.Series(var_fc, index=port.index[ROLLING_WINDOW:])
    actual = pd.Series(actual, index=port.index[ROLLING_WINDOW:])
    n = len(actual)
    x = int((actual < -var_fc).sum())
    lr, pval = kupiec_pvalue(x, n, a)
    res["backtest"] = {"n_days": n, "breaches": x, "breach_rate": x / n,
                       "expected_rate": a, "kupiec_LR": lr, "kupiec_pvalue": pval}
    print(f"\nOut-of-sample backtest ({ROLLING_WINDOW}-day rolling window, {n} days):")
    print(f"  Breaches {x} ({x/n:.1%}) vs expected {a:.0%}")
    print(f"  Kupiec test: LR = {lr:.2f}, p-value = {pval:.3f} "
          f"({'consistent with 5%' if pval > 0.05 else 'model rejected at 5% level'})")

    with open("results.json", "w") as f:
        json.dump(res, f, indent=2, default=float)
    print("\nSaved results.json")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(port * 100, bins=60, color="#1F3864", alpha=0.85)
    ax.axvline(-hist * 100, color="red", ls="--", label=f"Historical VaR {CONFIDENCE:.0%}: -{hist:.2%}")
    ax.axvline(-es * 100, color="orange", ls="--", label=f"Expected shortfall: -{es:.2%}")
    ax.set_xlabel("Daily portfolio return (%)"); ax.set_ylabel("Days")
    ax.set_title("Portfolio daily returns and VaR" + (" (SIMULATED DATA)" if args.demo else ""))
    ax.legend(); fig.tight_layout(); fig.savefig("var_chart.png", dpi=150)
    print("Saved var_chart.png")


if __name__ == "__main__":
    main()

# Portfolio Volatility and Value-at-Risk (Python)

**File:** `portfolio_risk_v2.py`

This script measures how risky a small stock portfolio is. It calculates annualized volatility, the correlation between holdings, how much of the portfolio's risk comes from each holding, and 1-day Value-at-Risk (VaR), which is the loss a portfolio is unlikely to exceed on a normal day. It also tests whether the VaR model holds up on data it hasn't seen.

### Methods

- **Historical VaR:** the loss at the 5th percentile of actual past daily portfolio returns. It makes no assumption about the shape of returns.
- **Parametric VaR:** assumes returns follow a normal distribution.
- **Monte Carlo VaR:** simulates 100,000 days of returns using the historical mean and covariance matrix.
- **Expected Shortfall:** the average loss on the worst 5% of days. It shows how bad the tail is, not just where it starts.
- **Risk contribution:** the share of total portfolio volatility each holding causes, which can differ from its weight.
- **Out-of-sample backtest:** each day's VaR is estimated only from the prior year of returns, then compared with what actually happened. A Kupiec test checks whether the breach rate matches the 5% we expect.

### Portfolio used

LMT 25%, HON 20%, SPY 25%, JPM 15%, MSFT 15%, with $100,000 invested. These are illustrative holdings across defense, industrials, financials, technology and the broad market. Edit the tickers and weights at the top of the script to test any portfolio.

### How to run

```bash
pip install yfinance pandas numpy scipy matplotlib
python portfolio_risk_v2.py                  # downloads 4 years of prices from Yahoo Finance
python portfolio_risk_v2.py --csv prices.csv # or use your own price file
python portfolio_risk_v2.py --demo           # simulated prices, to test the code only
```

The script saves `results.json` (all numbers) and `var_chart.png` (the return distribution with VaR lines).

### Results

Results from running the script on real Yahoo Finance prices, November 17, 2022 to November 17, 2026 (1,002 daily returns), with the default portfolio above.

| Measure | Value |
|---|---|
| Date range | Nov 17, 2022 – Nov 17, 2026 |
| Annualized portfolio volatility | 14.1% (vs. 21.6% weighted-average of the individual stocks) |
| 1-day 95% VaR (historical) | 1.42% ($1,418) |
| 1-day 95% VaR (parametric) | 1.41% ($1,409) |
| 1-day 95% VaR (Monte Carlo) | 1.40% ($1,401) |
| Expected Shortfall | 1.94% ($1,942) |
| Largest contributor to portfolio risk | LMT (24.3% of risk on a 25% weight) |
| Out-of-sample backtest: breaches vs. expected 5% | 45 of 750 days (6.0%) |
| Kupiec test p-value | 0.223 (not rejected at the 5% level) |

The diversification effect is large: the portfolio's volatility is about two-thirds of the average stock's, because the holdings are not highly correlated. The backtest breach rate is slightly above 5%, but the Kupiec test does not reject the model at the 5% level.

### Limitations

- Holdings are held at constant weights (no rebalancing), and returns are approximated as weighted daily log returns.
- Historical VaR assumes the recent past resembles the next day. It can miss sudden regime shifts.
- The parametric method understates tail risk when returns are fat-tailed.
- VaR says nothing about how large losses can get beyond the cutoff. That is why Expected Shortfall is included.
- Only one horizon (1 day) and one confidence level (95%) are used. Both are easy to change in the script.

---

I built this to practice the risk measurement skills used in financial risk and portfolio management. I work in financial reporting and investment analysis at La Fábrica PR LLC, and I am completing my B.B.A. in Finance at the University of Puerto Rico, Mayagüez campus. I would welcome feedback.

    

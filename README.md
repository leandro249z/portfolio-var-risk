#Portfolio Volatility and Value-at-Risk (Python)

File: portfolio_risk_v2.py

This script measures how risky a small stock portfolio is. It calculates annualized volatility, the correlation between holdings, how much of the portfolio's risk comes from each holding, and 1-day Value-at-Risk (VaR), which is the loss a portfolio is unlikely to exceed on a normal day. It also tests whether the VaR model holds up on data it hasn't seen.

Methods
Historical VaR: the loss at the 5th percentile of actual past daily portfolio returns. It makes no assumption about the shape of returns.
Parametric VaR: assumes returns follow a normal distribution.
Monte Carlo VaR: simulates 100,000 days of returns using the historical mean and covariance matrix.
Expected Shortfall: the average loss on the worst 5% of days. It shows how bad the tail is, not just where it starts.
Risk contribution: the share of total portfolio volatility each holding causes, which can differ from its weight.
Out-of-sample backtest: each day's VaR is estimated only from the prior year of returns, then compared with what actually happened. A Kupiec test checks whether the breach rate matches the 5% we expect.
Default portfolio (placeholder)

LMT 25%, HON 20%, SPY 25%, JPM 15%, MSFT 15%, with $100,000 invested. These weights are placeholders. Change them in the script to match your own portfolio.

How to run
bash
pip install yfinance pandas numpy scipy matplotlib
python portfolio_risk_v2.py                  # downloads 4 years of prices from Yahoo Finance
python portfolio_risk_v2.py --csv prices.csv # or use your own price file
python portfolio_risk_v2.py --demo           # simulated prices, to test the code only

The script saves results.json (all numbers) and var_chart.png (the return distribution with VaR lines).

Results

To be filled in after running the script on real data.

Measure	Value
Date range	
Annualized portfolio volatility	
1-day 95% VaR (historical)	
1-day 95% VaR (parametric)	
1-day 95% VaR (Monte Carlo)	
Expected Shortfall	
Largest contributor to portfolio risk	
Out-of-sample backtest: breaches vs. expected 5%	
Kupiec test p-value	
Limitations
Holdings are held at constant weights (no rebalancing), and returns are approximated as weighted daily log returns.
Historical VaR assumes the recent past resembles the next day. It can miss sudden regime shifts.
The parametric method understates tail risk when returns are fat-tailed.
VaR says nothing about how large losses can get beyond the cutoff. That is why Expected Shortfall is included.
Only one horizon (1 day) and one confidence level (95%) are used. Both are easy to change in the script.

I built this to practice the risk measurement skills used in financial risk and portfolio management. I work in financial reporting and investment analysis at La Fábrica PR LLC, and I am completing my B.B.A. in Finance at the University of Puerto Rico, Mayagüez campus. I would welcome feedback.

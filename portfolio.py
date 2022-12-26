import pandas as pd
import datetime
import utils.get_data as gd
import numpy as np
from matplotlib import pyplot as plt


class portfolio:
    def __init__(
        self,
        df: pd.DataFrame,
    ):
        self.tickers = df.index.to_list()
        self.weights = df["count"] / sum(df["count"])

    def get_prices(self, start_date: str = None, end_date: str = None):
        if None not in (start_date, end_date):
            self.all_prices = gd.get_historical_prices(
                self.tickers, start_date=start_date, end_date=end_date
            )
        else:
            self.all_prices = gd.get_historical_prices(self.tickers)

        self.adj_close = self.all_prices["Adj Close"]

        # Calculate the pct_changes. I take the log of the changes because log of returns is time additive.
        # So that a 0.1 change today and a -0.1 change tomorrow will give the same value of the stock as yesterday.
        self.pct_changes = self.adj_close.pct_change().apply(lambda x: np.log(1 + x))

        self.annual_std = self.pct_changes.std().apply(lambda x: x * np.sqrt(250))
        self.cov_matrix = self.pct_changes.cov()
        self.corr_matrix = self.pct_changes.corr()
        self.portfolio_variance = (
            self.cov_matrix.mul(self.weights, axis=0)
            .mul(self.weights, axis=1)
            .sum()
            .sum()
        )
        self.stock_values = self.adj_close.mul(df["count"], axis=1)
        self.portfolio_value = self.stock_values.sum(axis=1)
        self.expected_stock_returns = (
            self.adj_close.resample("Y").last().pct_change().mean()
        )
        self.expected_portfolio_returns = (
            self.weights * self.expected_stock_returns
        ).sum()
        self.assets = pd.concat(
            [self.expected_stock_returns, self.annual_std], axis=1
        )  # Creating a table for visualising returns and volatility of assets
        self.assets.columns = ["Returns", "Volatility"]

    def get_stock_info(self):
        stock_info_df = pd.DataFrame()
        for ticker in self.tickers:
            df = gd.get_stock_info(ticker)
            stock_info_df = stock_info_df.join(df, how="outer")
        self.stock_info = stock_info_df

    def efficient_frontier(self, num_portfolios=10000):
        p_ret = []  # Define an empty array for portfolio returns
        p_vol = []  # Define an empty array for portfolio volatility
        p_weights = []  # Define an empty array for asset weights

        num_assets = len(self.tickers)

        for portfolio in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights = weights / np.sum(weights)
            p_weights.append(weights)
            returns = np.dot(
                weights, self.expected_stock_returns
            )  # Returns are the product of individual expected returns of asset and its
            # weights
            p_ret.append(returns)
            var = (
                self.cov_matrix.mul(weights, axis=0).mul(weights, axis=1).sum().sum()
            )  # Portfolio Variance
            sd = np.sqrt(var)  # Daily standard deviation
            ann_sd = sd * np.sqrt(250)  # Annual standard deviation = volatility
            p_vol.append(ann_sd)

        data = {"Returns": p_ret, "Volatility": p_vol}

        for counter, symbol in enumerate(self.tickers):
            # print(counter, symbol)
            data[symbol + " weight"] = [w[counter] for w in p_weights]
        self.efficient_frontier_portfolios = pd.DataFrame(data)
        self.efficient_frontier_portfolios.plot.scatter(
            x="Volatility",
            y="Returns",
            marker="o",
            s=10,
            alpha=0.3,
            grid=True,
            figsize=[10, 10],
        )


if __name__ == "__main__":
    df = gd.get_personal_data()
    test_dict = {"AAPL": [0.1], "NKE": [0.2], "GOOGL": [0.5], "AMZN": [0.2]}
    test_df = pd.DataFrame.from_dict(test_dict, orient="index")
    p.tickers = test_df.index.to_list()
    test_df[0]
    p.weights = test_df[0]

    p = portfolio(df)
    p.get_stock_info()
    p.stock_info.loc["last_updated"]
    p.get_prices()
    p.stock_values.sum(axis=1)
    p.efficient_frontier(10000)

p.efficient_frontier_portfolios.plot.scatter(
    x="Volatility",
    y="Returns",
    marker="o",
    s=10,
    alpha=0.3,
    grid=True,
    figsize=[10, 10],
)
plt.subplots(figsize=[10, 10])

plt.scatter(
    p.efficient_frontier_portfolios["Volatility"],
    p.efficient_frontier_portfolios["Returns"],
    marker="o",
    s=10,
    alpha=0.3,
)
min_vol_port = p.efficient_frontier_portfolios.iloc[
    p.efficient_frontier_portfolios["Volatility"].idxmin()
]
plt.scatter(min_vol_port[1], min_vol_port[0], color="r", marker="*", s=500)
plt.show()
p.efficient_frontier_portfolios

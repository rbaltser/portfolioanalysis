import pandas as pd
import pandas_datareader as pdr
import yfinance as yf
import numpy as np
import yaml
from datetime import date


def retrieve_data(path):
    df = pd.read_csv(path, index_col=0)
    return df


def save_data(df: pd.DataFrame, address: str) -> None:
    df.to_csv("data\stock_info.csv")
    return


def get_stock_info(ticker: str) -> pd.DataFrame:
    df = pd.read_csv("data\stock_info.csv", index_col=0)
    if ticker not in df.columns:
        stock_ticker = yf.Ticker(ticker)
        stock_data = pd.DataFrame.from_dict(
            stock_ticker.info, orient="index", columns=[ticker]
        )
        stock_data.loc["last_updated"] = date.today()
        df = df.join(stock_data, how="outer")
        save_data(df)
    else:
        stock_data = df[ticker]
    return stock_data


def get_historical_prices(
    tickers: list, start_date: str = None, end_date: str = None
) -> pd.DataFrame:
    if None not in (start_date, end_date):
        data = yf.download(tickers, start=start_date, end=end_date)
    else:
        data = yf.download(tickers, period="1y")
    return data


def get_personal_data():
    path = "config\config.yaml"
    with open(path) as file:
        stocks = yaml.load(file, Loader=yaml.FullLoader)
        data = pd.DataFrame(pd.json_normalize(stocks).transpose())
        data.columns = ["count"]

    # get recent historical data
    # stock_prices = yf.download(data.index.tolist(), period="1mo")["Adj Close"]
    # merge dataframe with current price
    # stock_data = data.join(stock_prices.iloc[-1, :])
    # name columns
    # stock_data.columns = ["count", "current price"]
    # calculate current value of assets
    # stock_data["value"] = stock_data["count"] * stock_data["current price"]
    # calculate current weights of portfolio
    # stock_data["weight"] = stock_data["value"] / sum(stock_data["value"])
    # return stock_data
    return data

import pandas as pd
import utils.get_data as gd


start_date = "2021-01-01"
end_date = "2022-12-12"
portfolio = gd.get_personal_data()
stock_data = gd.get_historical_prices(portfolio.index.tolist(), start_date=start_date, end_date=end_date)
stock_data['Adj Close']

data

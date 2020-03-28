import pandas as pd
from src.data.make_dataset import get_data_from_yahoo
from datetime import datetime


def screen_uptrend(use_cache: bool = False):

    if use_cache:
        df = get_data_from_yahoo(save_csv=False)
    else:
        df = pd.read_csv('data/raw/filter.csv',
                         index_col='Date', parse_dates=True)

    tickers = df.columns.to_list()

    sma_used = [50, 200]

    screening_results = []

    for ticker in tickers:
        ticker_df = pd.DataFrame(df.loc[:, ticker].copy())

        for sma in sma_used:
            ticker_df = ticker_df.ffill()
            ticker_df.loc[:, "SMA_" + str(sma)] = \
                round(ticker_df.rolling(window=sma).mean(), 2)

        currentClose = ticker_df[ticker][-1]
        moving_average_50 = ticker_df["SMA_50"][-1]
        moving_average_200 = ticker_df["SMA_200"][-1]
        moving_average_200_20 = ticker_df["SMA_200"][-20]

        if currentClose > moving_average_50:
            if currentClose > moving_average_200:
                if moving_average_200 > moving_average_200_20:
                    screening_results.append({'Stock': ticker,
                                              "Close": currentClose,
                                              "50 Day MA": moving_average_50,
                                              "200 Day MA": moving_average_200,
                                              '200 Day Up': moving_average_200_20})

    return pd.DataFrame(screening_results)


if __name__ == "__main__":
    screen_uptrend(use_cache=False)

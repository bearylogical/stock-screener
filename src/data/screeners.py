import pandas as pd
from src.data.make_dataset import get_data_from_yahoo
from datetime import datetime
import numpy as np


def rma(x, n, y0):
    a = (n-1) / n
    ak = a**np.arange(len(x)-1, -1, -1)

    return np.append(y0,
                     np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1))


def get_rsi(df, n_rsi=14):

    df = df.dropna(axis=0 ,how='all')
    df_copy = df.reset_index().copy()
    
    df_copy['change'] = df_copy.iloc[:, 1].diff()
    df_copy['gain'] = df_copy.change.mask(df_copy.change < 0, 0.0)
    df_copy['loss'] = -df_copy.change.mask(df_copy.change > 0, -0.0)

    df_copy.loc[n_rsi:, 'avg_gain'] = rma(
        df_copy.gain[n_rsi+1:].values,
        n_rsi,
        df_copy.loc[:n_rsi, 'gain'].mean())

    df_copy.loc[n_rsi:, 'avg_loss'] = rma(
        df_copy.loss[n_rsi+1:].values,
        n_rsi,
        df_copy.loc[:n_rsi, 'loss'].mean())

    df_copy['rs'] = df_copy.avg_gain / df_copy.avg_loss
    df_copy[f'rsi_{n_rsi}'] = 100 - (100 / (1 + df_copy.rs))

    return df_copy


def screen_bounce(use_cache: bool = True):

    if use_cache:
        df = pd.read_csv('data/raw/filter.csv',
                         index_col='Date', parse_dates=True)
    else:
        df = get_data_from_yahoo(save_csv=False)

    tickers = df.columns.to_list()

    screening_results = []

    for ticker in tickers:
        ticker_df = pd.DataFrame(df.loc[:, ticker].copy())

        currentClose = ticker_df[ticker][-1]
        rsi_df = get_rsi(ticker_df)
        RSI = rsi_df['rsi_14'].iloc[-1]

        if RSI < 30:
            screening_results.append({'Stock': ticker,
                                      "Close": currentClose,
                                      "RSI": RSI})

    return pd.DataFrame(screening_results)


def screen_uptrend(use_cache: bool = True):

    if use_cache:
        df = pd.read_csv('data/raw/filter.csv',
                         index_col='Date', parse_dates=True)
    else:
        df = get_data_from_yahoo(save_csv=False)

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
    screen_bounce(use_cache=True)

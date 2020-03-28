# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import yfinance as yf


def get_snp_500_companies_list(save_csv=True):
    """gets the list of fortune 500 companies from wikipedia

    Keyword Arguments:
        save_csv {bool} -- save dataframe to csv (default: {True})

    Returns:
        [dataframe] -- dataframe containing the companies
    """
    URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    res = requests.get(URL)
    soup = BeautifulSoup(res.content, 'html.parser')
    tables = soup.find_all('table')
    table = tables[0]  # first table

    # Convert to df:
    df_SP500 = pd.read_html(str(table), header=0, flavor='html5lib')[0]
    df_SP500 = df_SP500.rename(columns={'Security': 'Company Name'})
    if save_csv:
        df_SP500.to_csv('../../data/raw/sp500.csv')

    return df_SP500


def get_data_from_yahoo(save_csv=True):

    df = get_snp_500_companies_list(save_csv=False)

    year = 2018
    month = 1
    day = 1

    min_date = datetime(year, month, day)

    tickers = df.Symbol.to_list()
    data = yf.download(tickers=" ".join(tickers),
                       period="5Y")

    filtered_data = data.loc[min_date:, 'Adj Close']
    
    if save_csv:
        filtered_data.to_csv('data/raw/finance_data.csv')

    return filtered_data


def get_today_fear_index():
    # Sentiment Screener - Look for a Market Bounce when Sentiment is below 20:
    URL = "https://money.cnn.com/data/fear-and-greed/"
    res = requests.get(URL)
    soup = BeautifulSoup(res.content, 'html.parser')

    # Find Data Section of Interest:
    Greed_Now = soup.find('div', attrs={'class': 'modContent feargreed'})

    greeds = Greed_Now.find_all('li')

    greed_dict = {
        'Present Value': '',
        'Previous Day': '',
        '1W': '',
        '1M': '',
        '1Y': ''
    }

    for idx, k in enumerate(greed_dict.keys()):
        text = greeds[idx].text
        val = re.search(r"(?<=\:)(.*?)(?=\()", text)
        greed_dict[k] = int(val.group())

    return pd.DataFrame(greed_dict, index=[datetime.now()])


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()

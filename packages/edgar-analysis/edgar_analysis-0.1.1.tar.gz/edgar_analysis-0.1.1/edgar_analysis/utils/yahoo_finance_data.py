"""yahoo_finance_data.py"""

import pandas as pd
from typing import List, Union, Optional
import logging

import yfinance as yf

from edgar_analysis.utils.tools import last_day_of_month


YF_BALANCE_SHEET_NAME = 'balance_sheet'
YF_INCOME_STATEMENT_NAME = 'income_statement'
YF_CASHFLOW_STATEMENT_NAME = 'cashflow_statement'

# Logger
formatter = logging.Formatter('%(asctime)s : %(module)s : %(funcName)s : %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)  # Set level specifically for this logger


def get_yf_balance_sheet(ticker: str, period: str = None) -> pd.DataFrame:
    """
    Downloads balance sheet from Yahoo Finance.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g., 'AAPL' for Apple)
    - period (str): 'annual' or 'quarterly' data

    Returns:
    - pandas.DataFrame: index=accounting names, columns=data per date
    """
    return get_yf_financial_statement_dataframe(ticker=ticker, statement_type=YF_BALANCE_SHEET_NAME, period=period)


def get_yf_income_statement(ticker: str, period: str = None) -> pd.DataFrame:
    """
    Downloads income statement from Yahoo Finance.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g., 'AAPL' for Apple)
    - period (str): 'annual' or 'quarterly' data

    Returns:
    - pandas.DataFrame: index=accounting names, columns=data per date
    """
    return get_yf_financial_statement_dataframe(ticker=ticker, statement_type=YF_INCOME_STATEMENT_NAME, period=period)


def get_yf_cashflow_statement(ticker: str, period: str = None) -> pd.DataFrame:
    """
    Downloads cash-flow statement from Yahoo Finance.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g., 'AAPL' for Apple)
    - period (str): 'annual' or 'quarterly' data

    Returns:
    - pandas.DataFrame: index=accounting names, columns=data per date
    """
    return get_yf_financial_statement_dataframe(ticker=ticker, statement_type=YF_CASHFLOW_STATEMENT_NAME, period=period)


def get_yf_financial_statement_dataframe(ticker: str, statement_type: Optional[Union[str, List[str]]] = None,
                                         period: str = None):
    """
    Downloads financial statements from Yahoo Finance with formatted column headers:
    - For balance sheet: 'instant_yyyy-mm-dd'
    - For income/cashflow statements (annual): 'duration_yyyy-mm-dd__12m'
    - For income/cashflow statements (quarterly): 'duration_yyyy-mm-dd__3m'

    When period is None, returns concatenated DataFrame with both annual and quarterly data.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g., 'AAPL' for Apple)
    - statement_type (str or list): Type of statement to download ('balance_sheet', 'cashflow_statement', 'income_statement')
                                   or list of these types
    - period (str): 'annual', 'quarterly', or None for both

    Returns:
    - dict or pandas.DataFrame: If multiple statement types requested, returns dict with statement_type
                               as keys and DataFrames as values. If single statement type requested,
                               returns just the DataFrame.
    """
    # Validate inputs
    valid_statement_types = [YF_BALANCE_SHEET_NAME, YF_INCOME_STATEMENT_NAME, YF_CASHFLOW_STATEMENT_NAME]
    if statement_type is None:
        statement_type = valid_statement_types.copy()

    # Convert single statement type to list for uniform processing
    if isinstance(statement_type, str):
        statement_type = [statement_type]

    for stmt in statement_type:
        if stmt.lower() not in valid_statement_types:
            raise ValueError(f"statement_type must be one of {valid_statement_types}")

    if period is not None:
        period = period.lower()
        if period not in ['annual', 'quarterly']:
            raise ValueError("period must be 'annual', 'quarterly', or None for both")

    # Get the stock data
    logger.info(f"Loading Yahoo Finance data for {ticker.upper()}")
    stock = yf.Ticker(ticker)
    result = {}

    for stmt in statement_type:
        # Initialize list to store all dataframes (annual and quarterly if period is None)
        all_data = []

        # Determine which periods to fetch
        periods_to_fetch = ['annual', 'quarterly'] if period is None else [period]

        for p in periods_to_fetch:
            logger.info(f"Fetch {p} {stmt.replace('_', ' ').capitalize()} for {ticker.upper()}")
            # Get the requested statement
            if stmt == YF_BALANCE_SHEET_NAME:
                data = stock.balance_sheet if p == 'annual' else stock.quarterly_balance_sheet
            elif stmt == YF_CASHFLOW_STATEMENT_NAME:
                data = stock.cashflow if p == 'annual' else stock.quarterly_cashflow
            elif stmt == YF_INCOME_STATEMENT_NAME:
                data = stock.financials if p == 'annual' else stock.quarterly_financials
            else:
                raise ValueError(f"{stmt} is not a valid financial statement")

            # Format column headers based on statement type and period
            formatted_columns = []
            for date_col in data.columns:
                end_date_str = date_col.strftime('%Y-%m-%d')
                months = 12 if p == 'annual' else 3
                start_date = last_day_of_month(any_day=date_col, month_offset=-months) + pd.DateOffset(days=1)
                start_date_str = start_date.strftime('%Y-%m-%d')
                if stmt == YF_BALANCE_SHEET_NAME:
                    formatted_columns.append(f'instant_{end_date_str}')
                else:
                    suffix = '__12m' if p == 'annual' else '__3m'
                    formatted_columns.append(f'duration_{start_date_str}_{end_date_str}{suffix}')

            # Create new dataframe with formatted columns
            formatted_data = pd.DataFrame(data.values, index=data.index, columns=formatted_columns)
            all_data.append(formatted_data)

        # Concatenate if we have multiple periods
        if len(all_data) > 1:
            # Use outer join to keep all rows from both periods
            combined_data = pd.concat(all_data, axis=1)
            # Sort columns chronologically
            combined_data = combined_data[sorted(combined_data.columns)]
            # Drop duplicate columns (keep the first instance)
            duplicated_columns = combined_data.columns.duplicated()
            result[stmt] = combined_data.loc[:, ~duplicated_columns].copy()
        else:
            result[stmt] = all_data[0]

    # Return single DataFrame if only one statement requested, otherwise return dict
    return result if len(result) > 1 else result[statement_type[0]]


def main():
    pd.set_option('display.max_rows', None)

    ticker = 'wmt'
    yf_bs = get_yf_balance_sheet(ticker=ticker)
    print(yf_bs)

if __name__ == '__main__':
    main()

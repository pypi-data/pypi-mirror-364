"""main.py
Works with edgartools==3.15.1
"""

from typing import List, Union, Dict

import numpy as np
import pandas as pd
import datetime
import logging

from edgar import Company, XBRL

from edgar_analysis.utils.data_extractor import DataExtractor
from edgar_analysis.financial_statements.accounting_items_config import AccountingItem, ItemType
from edgar_analysis.financial_statements.income_statement import REVENUE
from edgar_analysis.financial_statements.balance_sheet import TOTAL_ASSETS
from edgar_analysis.utils.yahoo_finance_data import get_yf_financial_statement_dataframe

from edgar_analysis.utils.synonyms import ANNUAL_SYNONYMS, QUARTERLY_SYNONYMS, TTM_SYNONYMS
from edgar_analysis.utils.data_calculation import ObservationFrequencyDataCalculator

# Logger
formatter = logging.Formatter('%(asctime)s : %(module)s : %(funcName)s : %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)  # Set level specifically for this logger

ANNUAL = 'annual'
QUARTERLY = 'quarterly'
TTM = 'ttm'


class CompanyAnalysis:
    """
    Class definition of CompanyAnalysis
    * Load financials with caching (e.g. when you have downloaded latest 4 filings, no need to download again if you
    only need latest 2)
    *  Get annual, quarterly or trailing twelve month data for all three financial statements
    """

    def __init__(self, ticker: str):
        self._ticker = ticker.upper()
        company = Company(self.ticker)
        if company.not_found:
            raise ValueError(f"No SEC registered company found for the ticker '{self.ticker}'.")
        elif company.latest_tenk is None or company.latest_tenq is None:
            raise ValueError(f"There are no 10-Ks or 10-Qs linked to ticker {self.ticker}. \nCompany might be an ADR which "
                             f"is not yet supported.")
        else:
            self._company = company
        self._filings = self.company.get_filings(form=['10-K', '10-Q'])  # This form filter does not work (see TSLA)
        self._filings_meta_data_df = self.filings.data.to_pandas()
        self._all_reporting_dates = self.filings_meta_data_df[self.filings_meta_data_df['form'].isin(['10-Q', '10-K'])]['reportDate'].tolist()
        self._all_fy_reporting_dates = self.filings_meta_data_df[self.filings_meta_data_df['form'] == '10-K']['reportDate'].tolist()
        self._data_extractor = DataExtractor()
        self._cached_acc_no_xbrl_map = {}
        logger.debug(f"Successfully initialized a CompanyAnalysis object for ticker {ticker.upper()}")

    # XBRL statements and handle filings ---------------------------------------------------
    def _get_acc_no_xbrl_map(self, periods: int, annual_statements: bool) -> Dict[str, XBRL]:
        """
        Returns a list of relevant XBRL for relevant filings based on the number of periods and if it is annual
        only or not
        :param periods: int
        :param annual_statements: bool
        :return: List of XBRL
        """
        # Always assume that the XBRL are sorted by reporting date
        form = ['10-K'] if annual_statements else ['10-K', '10-Q']
        requested_filings = [f for f in self.filings if f.form in form][:periods]

        # Update xbrl list if applicable
        self._update_xbrl_list(filings=requested_filings)

        # For the relevant accession numbers
        req_accession_numbers = self._get_accession_no_from_filings(filings=requested_filings)
        result = {
            acc_no: self._cached_acc_no_xbrl_map[acc_no] for acc_no in req_accession_numbers
        }
        return result

    def _update_xbrl_list(self, filings) -> None:
        """
        For the specified filings, check to see if there are already corresponding XBRL for filings. If XBRL are missing
        for some filings, load those XBRL and store in cach
        :param filings: entity filings
        :return: None
        """
        # Get a list of filings that has not yet been cached
        non_cached_filings = self._get_non_cached_filings(requested_filings=filings)

        # If there are filings missing, load new XBRL and store them in cache
        if non_cached_filings:
            logger.debug(f"Extract XBRL from {len(non_cached_filings)} filing(s)")
            non_cached_xbrl_map = {
                f.accession_no: XBRL.from_filing(f)
                for f in non_cached_filings
            }
            logger.debug(f"Store {len(non_cached_xbrl_map)} XBRL in cache")
            self._cached_acc_no_xbrl_map.update(non_cached_xbrl_map)

    def _get_non_cached_filings(self, requested_filings: list) -> list:
        """
        Returns a list of filings that has not yet been cached
        :param requested_filings: list of filings
        :return: list of filings
        """

        if not self._cached_acc_no_xbrl_map:
            return requested_filings

        # Get accession numbers for comparison
        non_cached_filings = [f for f in requested_filings
                              if f.accession_no not in self._cached_acc_no_xbrl_map.keys()]
        return non_cached_filings

    @staticmethod
    def _get_accession_no_from_filings(filings: list):
        """
        Returns a list of accession numbers for specified filings
        :param filings: list of entity filing
        :return: list
        """
        return [f.accession_no for f in filings]

    # @staticmethod
    # def _sort_xbrl_statements(xbrl_statements: list) -> list:
    #     """
    #     Sorts the specified XBRL statements (earliest to oldest reporting date)
    #     :return: None
    #     """
    #     return sorted(xbrl_statements.copy(), key=lambda x: x.statements.xbrls.entity_info['document_period_end_date'], reverse=True)

    def clear_cache(self):
        """Clears all cached data"""
        logger.debug("Clear cache")
        self._cached_acc_no_xbrl_map = {}

    @staticmethod
    def _get_standardized_frequency(frequency: str) -> str:
        """
        Returns a standardized observation frequency str
        :param frequency: str
        :return: str
        """
        frequency_lower_no_blanks = frequency.lower().replace(' ', '').replace('_', '')
        if frequency_lower_no_blanks in ANNUAL_SYNONYMS:
            return ANNUAL
        elif frequency_lower_no_blanks in QUARTERLY_SYNONYMS:
            return QUARTERLY
        elif frequency_lower_no_blanks in TTM_SYNONYMS:
            return TTM
        else:
            raise ValueError(f"{frequency} is not a recognized observation frequency. Use either '{ANNUAL}', "
                             f"'{QUARTERLY}' or '{TTM}'")

    # Getting data and perform edgar_analysis ---------------------------------------------------
    def get_accounting_items(self, accounting_item: Union[List[AccountingItem], AccountingItem], periods: int, frequency: str,
                             dates_as_cols: bool = False, dates_ascending_order: bool = True) -> pd.DataFrame:
        """
        Retrieve accounting items data for specified periods and frequency.

        Processes financial statement data to return accounting metrics in either:
        - Annual figures
        - Quarterly figures
        - Trailing Twelve Month (TTM) calculations

        Parameters
        ----------
        accounting_item : Union[str, List[str]]
            Accounting item(s) to retrieve. Can be a single item (AccountingItem) or multiple items (List[AccountingItem]).

        periods : int
            Number of historical periods to retrieve. For TTM calculations, additional periods
            are automatically fetched to ensure accurate rolling calculations.

        frequency : str
            The observation frequency for the returned data. Valid options are:
            - 'annual' - Annual financial statements
            - 'quarterly' - Quarterly financial statements
            - 'ttm' - Trailing Twelve Month calculations

        dates_as_cols : bool, optional
            If True, returns data with dates as columns (wide format).
            If False (default), returns data with dates in the index (long format).

        dates_ascending_order : bool, optional
            If True (default), returns data with dates in ascending order (oldest first).
            If False, returns dates in descending order (newest first).

        Returns
        -------
        pd.DataFrame
            DataFrame containing the requested accounting items with the following characteristics:
            - Index: Accounting items (if dates_as_cols=True) or Dates (if dates_as_cols=False)
            - Columns: Dates (if dates_as_cols=True) or Accounting items (if dates_as_cols=False)
            - Values: The numerical accounting values for each item/period combination

        Notes
        -----
        - For TTM calculations, the method automatically fetches 3 additional periods of data
          to ensure accurate rolling calculations.
        - The method handles both instant (balance sheet) and duration (income/cash flow) items.
        - All returned values maintain their original units (e.g., millions) as reported in the filings.

        Examples
        --------
        > analyzer = CompanyAnalysis('AAPL')
        > # Get annual revenue for last 5 years
        > analyzer.get_accounting_items(REVENUE, 5, 'annual')
        > # Get quarterly Cost of Goods Sold for last 8 quarters (newest first)
        > analyzer.get_accounting_items(COGS, 8, 'quarterly', dates_ascending_order=False)
        > # Get TTM net income for last 4 periods
        > analyzer.get_accounting_items(NET_INCOME, 4, 'ttm')
        """
        # Adjust the inputs
        accounting_item = [accounting_item] if not isinstance(accounting_item, list) else accounting_item
        frequency = self._get_standardized_frequency(frequency=frequency)
        adj_periods = periods + 3 if frequency == TTM else periods  # Use 3 more filings when calc. ttm

        # Extract the data
        extracted_acc_itm_df = self._get_extracted_dataframe(
            accounting_item=accounting_item,
            adj_periods=adj_periods,
            frequency=frequency,
        )

        # Get the correct data columns based on the observation frequency (calculation is made when applicable)
        report_dates = self.all_fy_reporting_dates if frequency == ANNUAL else self._all_reporting_dates
        data_calculator = ObservationFrequencyDataCalculator(
            df=extracted_acc_itm_df,
            report_dates=report_dates
        )

        # Calculate quarterly values
        if frequency in [QUARTERLY, TTM]:

            qtr_acc_itm_df = data_calculator.get_quarterly_data(periods=adj_periods)

            if frequency == TTM:
                # Rolling across the columns by first transposing the result, sort index and then do the reverse
                # Only do this for data that is not instant like balance sheet items
                result_df = self._calculate_trailing_twelve_month(quarterly_df=qtr_acc_itm_df, accounting_item=accounting_item).iloc[:, :periods]  # Only include the requested periods
            else:
                # Result stays the same
                result_df = qtr_acc_itm_df.iloc[:, :periods]
        else:
            # Just extract the annual values
            result_df = data_calculator.get_annual_data(periods=periods)

        # Re-order the accounting items in the original order
        long_names = [item.name for item in accounting_item]
        result_df = result_df.loc[long_names, :].copy()

        # Format final result
        result_df = self._reformat_result_df(result_df=result_df, dates_as_cols=dates_as_cols,
                                             dates_ascending_order=dates_ascending_order)
        return result_df

    def _get_extracted_dataframe(self, accounting_item: List[AccountingItem], adj_periods: int, frequency: str):
        """
        Returns a DataFrame with extracted data for each accounting item. Updates the cached accession number XBRL map.
        :param accounting_item: list of AccountingItem
        :param adj_periods: int should be the normal periods + 3 in case of TTM
        :param frequency: str
        :return: DataFrame
        """
        logger.debug(f"Set up a data extractor and extract the latest {adj_periods} '{frequency.title()}' data for "
                     f"'%s'" % "', '".join([item.name for item in accounting_item]))
        # Extract the specified accounting items by first get the required xbrl
        annual_statements_only = frequency == ANNUAL
        acc_no_xbrl_map = self._get_acc_no_xbrl_map(periods=adj_periods, annual_statements=annual_statements_only)

        # Create an EnhancedXBRLS object, give it to the data extractor, store extracted data in a DataFrame
        # Sort the XBRL by period_of_report
        xbrl_list = sorted(
            list(acc_no_xbrl_map.values()),
            key=lambda x: datetime.datetime.strptime(x.period_of_report, '%Y-%m-%d'),
            reverse=True
        )
        self._data_extractor.xbrl_list = xbrl_list
        # Initialize a data placeholder containing Yahoo finance data (if applicable)
        data_placeholder = self._get_yahoo_finance_data(accounting_item=accounting_item, periods=adj_periods,
                                                        frequency=frequency)
        extracted_acc_itm_df = self._data_extractor.extract(period_data_map=data_placeholder,
                                                            accounting_items=accounting_item)

        # Update the list of XBRL after data has been loaded
        acc_no_xbrl_map_post_work = dict(zip(list(acc_no_xbrl_map.keys()), self._data_extractor.xbrl_list))
        self._cached_acc_no_xbrl_map.update(acc_no_xbrl_map_post_work)

        return extracted_acc_itm_df

    def _get_yahoo_finance_data(self, accounting_item: List[AccountingItem], periods: int, frequency: str) -> dict:
        """
        Returns a dict with accounting item name as key and another dict(keys=period date str, values=data) as values
        E.g.
            {
            'Revenue':
                {
                    'duration_2021-01-01_2021-03-31__3m': 100000.0,
                    'duration_2021-01-01_2021-06-31__6m': 3500000.0,
                }
            }
        :param accounting_item: list of AccountingItem
        :param periods: int
        :param frequency: str
        :return:
        """
        if frequency == QUARTERLY and periods <= 4:
            period = QUARTERLY
        elif frequency == ANNUAL and periods <= 4:
            period = ANNUAL
        else:
            period = None

        result = {}
        statements = list(set([item.statement for item in accounting_item]))
        logger.info("Loading data from Yahoo Finance...")
        yf_data = get_yf_financial_statement_dataframe(ticker=self.ticker, statement_type=statements, period=period)
        logger.info("Done loading data from Yahoo Finance!")

        if len(statements) == 1 and isinstance(yf_data, pd.DataFrame):
            yf_data = {statements[0]: yf_data}

        for item in accounting_item:
            if item.yahoo_name:
                result[item.name] = yf_data[item.statement].loc[item.yahoo_name].dropna().to_dict()
            else:
                result[item.name] = {}

        return result

    @staticmethod
    def _calculate_trailing_twelve_month(quarterly_df: pd.DataFrame, accounting_item: List[AccountingItem]) -> pd.DataFrame:
        """
        Calculates rolling sum of four quarters. Checks so that calculation is only performed on accouning items that
        are measured over a period (e.g. revenues) and not when measured in one point in time (e.g. total assets)
        :param quarterly_df: DataFrame(index=accounting item names, cols=data columns with dates as names)
        :param item_type_map: dict(keys=accounting item name, values=item type 'duration' 'instant')
        :return: DataFrame(index=accounting item names, cols=data columns with dates as names)
        """
        logger.debug("Calculate trailing twelve months")
        # First split the accounting items in instant (e.g. total assets) and periodic (e.g. revenues) data
        # Boolean column that is True if instant else False
        item_type_map = {item.name: item.item_type
                         for item in accounting_item}
        quarterly_df['is_instant'] = quarterly_df.index.map(item_type_map) == ItemType.INSTANT
        non_instant_data = quarterly_df[~quarterly_df['is_instant']].copy().drop(columns=['is_instant'])
        non_instant_data = non_instant_data.T.sort_index().replace('', np.nan).apply(pd.to_numeric, errors='ignore')

        # Accounting item name, has nan map will need to be checked with a map weather or not nan are allowed
        has_nan_map = non_instant_data.isna().any()[non_instant_data.isna().any()].to_dict()
        fill_nan_zero = [item.name for item in accounting_item if item.name in has_nan_map.keys() and item.allow_na]
        # Replace NaN with 0 in specified columns
        non_instant_data.loc[:, fill_nan_zero] = non_instant_data.loc[:, fill_nan_zero].fillna(0)

        # After filling the nan that are allowed, check if nan exists
        items_with_nan = [name for name, has_nan in non_instant_data.isna().any().to_dict().items() if has_nan]
        if items_with_nan:
            logger.warning("When calculating trailing twelve months, NaN were found for '%s'" % "', '".join(items_with_nan))

        ttm_acc_itm_df = non_instant_data.rolling(window=4).sum()
        ttm_acc_itm_df = ttm_acc_itm_df.sort_index(ascending=False).T  # Sort and transpose back to og format
        instant_data = quarterly_df[quarterly_df['is_instant']].copy().drop(columns=['is_instant'])
        result = pd.concat([instant_data, ttm_acc_itm_df], axis=0).reindex(quarterly_df.index)
        return result

    @staticmethod
    def _reformat_result_df(result_df: pd.DataFrame, dates_as_cols: bool, dates_ascending_order: bool):
        """
        Returns a DataFrame that either sorts dates or sets dates as cols
        :param result_df: DataFrame(index=accounting items (str), cols=dates (str))
        :param dates_as_cols: bool (keeps dates as col headers else set accounting items as names)
        :param dates_ascending_order: bool if True sorts dates in ascending order (old to new)
        :return: DataFrame
        """
        df = result_df.copy()
        df.sort_index(axis=1, inplace=True, ascending=dates_ascending_order)
        if not dates_as_cols:
            df = df.T
        return df

    def get_revenues(self, periods: int, frequency: str, dates_as_cols: bool = False, dates_ascending_order: bool = True):
        return self.get_accounting_items(accounting_item=REVENUE, periods=periods, frequency=frequency,
                                         dates_as_cols=dates_as_cols, dates_ascending_order=dates_ascending_order)

    def get_total_assets(self, periods: int, frequency: str, dates_as_cols: bool = False, dates_ascending_order: bool = True):
        return self.get_accounting_items(accounting_item=TOTAL_ASSETS, periods=periods, frequency=frequency,
                                         dates_as_cols=dates_as_cols, dates_ascending_order=dates_ascending_order)

    # Property getters/setters ---------------------------------------------------
    @property
    def ticker(self):
        return self._ticker

    @ticker.setter
    def ticker(self, ticker: str):
        if ticker.upper() != self._ticker:
            logger.debug(f"Change ticker to {ticker.upper()}")
            self._ticker = ticker.upper()
            company = Company(self.ticker)
            if company.not_found:
                raise ValueError(f"No SEC registered corp. found for the ticker '{self.ticker}'.")
            elif company.latest_tenk is None or company.latest_tenq is None:
                raise ValueError(
                    f"There are no 10-Ks or 10-Qs linked to ticker {self.ticker}. \nCompany might be an ADR which "
                    f"is not yet supported.")
            else:
                self._company = company
            self._filings = self.company.get_filings(form=['10-K', '10-Q'])
            self._filings_meta_data_df = self.filings.data.to_pandas()
            self._filings_meta_data_df = self.filings.data.to_pandas()
            self._all_reporting_dates = self.filings_meta_data_df[self.filings_meta_data_df['form'].isin['10-K', '10-K']][
                'reportDate']
            self._all_fy_reporting_dates = self.filings_meta_data_df[self.filings_meta_data_df['form'] == '10-K'][
                'reportDate'].tolist()
            self._data_extractor = DataExtractor()
            self.clear_cache()

    @property
    def company(self):
        return self._company

    @property
    def filings(self):
        return self._filings

    @property
    def filings_meta_data_df(self):
        return self._filings_meta_data_df

    @property
    def all_reporting_dates(self):
        return self._all_reporting_dates

    @property
    def all_fy_reporting_dates(self):
        return self._all_fy_reporting_dates

    def __repr__(self):
        """Gives the precise representation so that the output can be recreated in code"""
        return f"{self.__class__.__name__}('{self.ticker}')"



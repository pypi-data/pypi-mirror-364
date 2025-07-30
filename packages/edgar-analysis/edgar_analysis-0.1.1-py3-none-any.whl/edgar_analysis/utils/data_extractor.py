"""data_extractor.py"""

import pandas as pd
import numpy as np
from typing import List as TypingList, Union, Literal
from itertools import combinations
import logging
from tabulate import tabulate

from edgar import XBRL

from edgar_analysis.financial_statements.accounting_items_config import StatementType, AccountingItem, ItemType

# Logger
formatter = logging.Formatter('%(asctime)s : %(module)s : %(funcName)s : %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)  # Set level specifically for this logger


class DataExtractor:
    """Class definition of DataExtractor"""

    def __init__(self, xbrl_list: TypingList[XBRL] = None, accounting_items: Union[TypingList[AccountingItem], AccountingItem] = None):
        logger.debug("Initialize an instance of DataExtractor")
        self.xbrl_list = xbrl_list
        self.accounting_items = accounting_items

        self._PASCAL_CASE_STATEMENT_MAP = {
            StatementType.INCOME: 'IncomeStatement',
            StatementType.BALANCE: 'BalanceSheet',
            StatementType.CASHFLOW: 'CashFlowStatement'
        }

    def _pre_extraction_check(self):
        """
        Raises an error if all is not OK before extraction
        :return:
        """
        if self.xbrl_list is None:
            raise ValueError("xbrl_list not specified or empty")

        if self.accounting_items is None:
            raise ValueError("accounting_items not specified")

    def check_period_data_map(self, period_data_map: dict) -> dict:
        """
        Checks so that period_data_map is correctly specified and returns an adjusted map like adding the accounting
        item name as a key on the first layer when there is only one accounting item
        :param period_data_map: dict
        :return: dict
        """

        item_names = [item.name for item in self.accounting_items]  # Names of all the accounting item names

        if period_data_map:
            if all(isinstance(v, dict) for v in period_data_map.values()):
                # Here the first level of keys needs to be the accounting item names
                for item_name_key in period_data_map.keys():
                    if item_name_key not in item_names:
                        raise ValueError(f"'{item_name_key}' needs to be one of '%s'" % "', '".join(item_names))
            elif all(isinstance(v, (float, int)) for v in period_data_map.values()):
                if len(self.accounting_items) > 1:
                    raise ValueError(f"Since there are {len(self.accounting_items)} accounting items, a period_data_map specified as a dict(keys=str, values=float) needs to have an accounting item name key")
                period_data_map = {self.accounting_items[0].name: period_data_map.copy()}
            else:
                raise ValueError("period_data_map is specified incorrectly")
        else:
            logger.debug("Empty period data map created")
            period_data_map = {name: {} for name in item_names}
        return period_data_map

    def extract(self, period_data_map: dict = None, accounting_items: Union[TypingList[AccountingItem], AccountingItem] = None) -> pd.DataFrame:
        """
        Extracts XBRL facts needed for each accounting item and returns result as a DataFrame(cols=data for each period
        dates, index=accounting item names)
        :param period_data_map: dict
        :param accounting_items: AccountingItem or list of AccountingItem
        :return: DataFrame
        """

        # --------------------------------------------------------------------------------------------------------------
        # Check and adjust inputs and attributes
        if accounting_items:
            self.accounting_items = accounting_items

        self._pre_extraction_check()
        result_placeholder = self.check_period_data_map(period_data_map=period_data_map)

        # --------------------------------------------------------------------------------------------------------------
        # Loop through each xbrl, extract the facts, reformat the data and store results in a dict to finally
        # concatenate all result into one DataFrame
        for xbrl in self.xbrl_list:

            for item in self.accounting_items:

                facts_df = self._get_xbrl_facts_dataframe(xbrl=xbrl, accounting_item=item)

                # Perform the matching filter dictated by the accounting item and pivot the result after adding correct
                # period dates
                pivot_filtered_df = self._filter_and_pivot_dataframe(df=facts_df, accounting_item=item)

                # Search if there are any past values that can be used to match
                if pivot_filtered_df.shape[0] > 1 and result_placeholder.get(item.name, False):
                    pivot_filtered_df = self.find_best_match_by_values(sec_df=pivot_filtered_df, values_dict=result_placeholder[item.name],
                                                                  allow_sum=item.can_be_sum)
                    logger.info(f"Result after matching with values: \n{tabulate(pivot_filtered_df, headers='keys', tablefmt='psql')}")

                # Drop 'concept' and 'label' and sum results if applicable
                if item.can_be_sum:
                    clean_result = pivot_filtered_df.drop(columns=['concept', 'label']).sum()
                else:
                    if pivot_filtered_df.shape[0] > 1:
                        logger.warning(f'Data returned {pivot_filtered_df.shap[0]} rows of data. The script will use the first row.')
                        logger.info(tabulate(pivot_filtered_df[['concept', 'label']], headers='keys', tablefmt='psql'))
                    clean_result = pivot_filtered_df.drop(columns=['concept', 'label']).iloc[0]

                # Update the result placeholder
                result_placeholder[item.name] = clean_result.to_dict() | result_placeholder[item.name]

        result_df = pd.DataFrame(result_placeholder).T  # Convert to a DataFrame
        result_df = result_df.loc[:, ~result_df.columns.duplicated()].copy()  # Drop duplicate cols
        return result_df

    def _get_xbrl_facts_dataframe(self, xbrl: XBRL, accounting_item: AccountingItem) -> pd.DataFrame:
        """
        Returns a DataFrame containing XBRL facts after some cleaning that will later be filtered
        :param xbrl: XBRL
        :param accounting_item: AccountingItem
        :return: DataFrame
        """
        logger.debug(f"Extract an XBRL facts DataFrame ({xbrl.entity_name} {xbrl.document_type} {xbrl.period_of_report})")
        pascal_case_statement = self._PASCAL_CASE_STATEMENT_MAP[accounting_item.statement]
        if accounting_item.allow_non_statement_data:
            facts_df = xbrl.query().to_dataframe()  # Loads the XBRL facts for one filing stored as a DataFrame

            # Drop statements other than the one that accounting item belongs to and nan (for notes data)
            facts_df = facts_df[facts_df['statement_type'].isin([pascal_case_statement, np.nan])].copy()
        else:
            facts_df = xbrl.query().by_statement_type(pascal_case_statement).to_dataframe()

        if not accounting_item.allow_dimension_data:
            # When not looking to include data coming from a dimension (segment or product line for example) drop
            # rows where a dimension col is not nan
            facts_df = self.drop_dimension_data_rows(df=facts_df)

        # Drop non-numerical data and duplicate rows
        clean_facts_df = self.clean_dataframe(df=facts_df)

        return clean_facts_df

    def _filter_and_pivot_dataframe(self, df: pd.DataFrame, accounting_item: AccountingItem):
        """
        Filters an XBRL facts DataFrame according to matching configuration for the specified accounting item. Result
        is pivoted such that columns will be 'concept, 'label' and the rest are date period cols with accounting data
        :param df: DataFrame
        :param accounting_item: AccountingItem
        :return: DataFrame
        """
        logger.debug("Filter and pivot XBRL facts DataFrame")
        # Perform the matching filter dictated by the accounting item
        filtered_df = accounting_item.filter_dataframe(df=df)

        # Filter based on accounting item being measured over a period or instant
        filtered_df = self.filter_accounting_periods(df=filtered_df, item_type=accounting_item.item_type)

        # Add a column called 'period'
        filtered_df = self._add_period_column(df=filtered_df)

        # Pivot so that cols are period with numeric_values as values
        pivot_filtered_df = (
            filtered_df.set_index(['concept', 'label', 'period'])['numeric_value']
            .unstack()
            .reset_index()
            .rename_axis(columns=None)
        )
        return pivot_filtered_df

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Returns a DataFrame after dropping rows where 'numeric_value' col is nan and removing duplicate rows
        :param df: DataFrame
        :return: DataFrame
        """
        logger.debug("Drop rows where 'numeric_value' is nan and drop duplicate rows (keeping the first)")
        # Drop non-numerical data
        df.dropna(subset=['numeric_value'], inplace=True)

        # Drop duplicate rows
        df = df.drop_duplicates()  # Default: keeps first occurrence
        return df

    @staticmethod
    def drop_dimension_data_rows(df: pd.DataFrame) -> pd.DataFrame:
        """
        When not looking to include data coming from a dimension (segment or product line for example) drop rows where a
        dimension col is not nan
        :param df: DataFrame
        :return: DataFrame
        """
        logger.debug("Drop dimension columns from the XBRL facts DataFrame")
        # Identify columns starting with dim_
        dim_cols = [col for col in df.columns if col.startswith('dim_')]

        # Drop rows where any 'dim_' column is not NaN
        filtered_df = df[~df[dim_cols].notna().any(axis=1)].copy()
        return filtered_df

    @staticmethod
    def filter_accounting_periods(df: pd.DataFrame,
                                  item_type: Union[Literal['instant', 'duration'], ItemType]) -> pd.DataFrame:
        """
        Returns a DataFrame where each row has been filtered based on weather or not the data is an instant or duration data
        If no row of data exist for the specified accounting item type, returns an empty DataFrame (keeping original cols)
        :param df: DataFrame
        :param item_type: ItemType or 'instant', 'duration'
        :return: DataFrame
        """
        logger.debug(f"Filter DataFrame rows for '{item_type}' accounting data")
        # Initialize empty DataFrame
        if item_type == ItemType.DURATION and all(col in df.columns for col in ['period_start', 'period_end']):
            duration_mask = df['period_start'].notna() & df['period_end'].notna()
            result_df = df[duration_mask].copy()
        elif item_type == ItemType.INSTANT and 'period_instant' in df.columns:
            result_df = df[df['period_instant'].notna()].copy()
        else:
            return pd.DataFrame(columns=df.columns)
        return result_df

    def _add_period_column(self, df) -> pd.DataFrame:
        """
        Add a column named 'period' with either duration or instant str
        :param df: DataFrame
        :return: DataFrame
        """
        logger.debug('Add period column')
        # Create a copy to avoid SettingWithCopyWarning
        df = df.copy()

        # Initialize period column with empty strings
        df.insert(0, 'period', '')

        # Case 1: Both period_start and period_end exist
        if all(col in df.columns for col in ['period_start', 'period_end']):
            period_mask = df['period_start'].notna() & df['period_end'].notna()
            df.loc[period_mask, :] = self._calculate_duration_period_column(df=df.loc[period_mask, :].copy())

        # Case 2: period_instant exists
        if 'period_instant' in df.columns:
            instant_mask = df['period_instant'].notna()
            df.loc[instant_mask & (df['period'] == ''), 'period'] = 'instant_' + df['period_instant']

        # For rows where period is still empty (no period columns or all NaN), leave as empty string
        return df

    @staticmethod
    def _calculate_duration_period_column(df):
        """
        Calculates the 'period' column based on period_start and period_end dates.
        Format: 'duration_[period_start]_[period_end]__[N]m' where N is the closest standard duration (3, 6, 9, or 12 months)

        Parameters:
        - df: pandas.DataFrame containing 'period_start' and 'period_end' columns

        Returns:
        - pandas.DataFrame with added 'period' column
        """
        logger.debug('Calculate duration of each period column')
        df = df.copy()
        # Make sure we have datetime objects
        df['period_start'] = pd.to_datetime(df['period_start'])
        df['period_end'] = pd.to_datetime(df['period_end'])

        # Calculate duration in months
        # 30.44 provides a balanced approximation of the average number of days in a month
        df['duration_months'] = ((df['period_end'] - df['period_start']).dt.days / 30.44).round().astype(int)

        # Round to nearest standard duration (3, 6, 9, or 12 months)
        def round_to_standard_duration(months):
            return min([3, 6, 9, 12], key=lambda x: abs(x - months))

        df['rounded_duration'] = df['duration_months'].apply(round_to_standard_duration)

        # Format the period string
        df['period'] = df.apply(
            lambda
                row: f"duration_{row['period_start'].strftime('%Y-%m-%d')}_{row['period_end'].strftime('%Y-%m-%d')}__{row['rounded_duration']}m",
            axis=1
        )

        # Convert datetime columns back to strings
        df['period_start'] = df['period_start'].dt.strftime('%Y-%m-%d')
        df['period_end'] = df['period_end'].dt.strftime('%Y-%m-%d')

        # Drop temporary columns
        df = df.drop(columns=['duration_months', 'rounded_duration'])
        return df

    @staticmethod
    def find_best_match_by_values(sec_df: pd.DataFrame, values_dict: dict, allow_sum: bool = False,
                                  max_combination_size: int = 5) -> pd.DataFrame:
        """
        Returns a DataFrame that has filtered rows based on overlapping data based on a dict

        Workflow:
        First Pass: Looks for exact single-row matches
        Second Pass: Checks for exact sum matches (if allow_sum=True)
        Third Pass:
            With allow_sum: Finds closest sum match (single or combined rows)
            Without allow_sum: Finds closest single-row match

        :param sec_df: DataFrame(cols='concept', 'label', period data cols)
        :param values_dict: dict(keys=period dates, values=value)
        :param allow_sum: bool If aTrue, checks combinations (1-5 rows) for the closest sum match, else single-row comp
        :param max_combination_size: int Smaller combination sizes is recommended for large DataFrames
        :return: DataFrame
        """
        logger.info(f"Attempts to find best match by values since {sec_df.shape[0]} rows remains after filtering")
        logger.info(tabulate(sec_df[['concept', 'label']], headers='keys', tablefmt='psql'))
        # Get numeric columns from SEC data
        sec_numeric = sec_df.select_dtypes(include=np.number)
        relevant_cols = [col for col in sec_numeric.columns if col in values_dict]

        # First pass: check for exact single matches
        for sec_col in relevant_cols:
            target_value = values_dict[sec_col]
            match_mask = sec_numeric[sec_col] == target_value
            if match_mask.sum() == 1:
                logger.info(f'Exact value match found at period {sec_col}')
                return sec_df[match_mask]

        # Second pass: if allow_sum, check combinations
        if allow_sum:
            for sec_col in relevant_cols:
                target_value = values_dict[sec_col]
                col_values = sec_numeric[sec_col]

                # Check combinations of increasing size
                for r in range(2, min(max_combination_size, len(sec_df)) + 1):
                    for idx_combo in combinations(sec_df.index, r):
                        if np.isclose(col_values.loc[list(idx_combo)].sum(), target_value):
                            result = sec_df.loc[list(idx_combo)].copy()
                            logger.info(f"Exact value match found at period {sec_col} where '%s' were summed" % ', '.join(list(result['concept'])))
                            return result

        # Third pass: find closest match (now includes combinations if allow_sum)
        best_match = None
        min_diff = np.inf

        for sec_col in relevant_cols:
            target_value = values_dict[sec_col]
            col_values = sec_numeric[sec_col]

            if allow_sum:
                # Check combinations for closest match
                for r in range(1, min(max_combination_size, len(sec_df)) + 1):
                    for idx_combo in combinations(sec_df.index, r):
                        current_sum = col_values.loc[list(idx_combo)].sum()
                        current_diff = abs(current_sum - target_value)

                        if current_diff < min_diff:
                            min_diff = current_diff
                            best_match = list(idx_combo)
            else:
                # Original single-row comparison
                current_diff = np.abs(col_values - target_value)
                if current_diff.min() < min_diff:
                    min_diff = current_diff.min()
                    best_match = [sec_df.index[np.argmin(current_diff)]]

        return sec_df.loc[best_match] if best_match else None

    @property
    def xbrl_list(self):
        return self._xbrl_list

    @xbrl_list.setter
    def xbrl_list(self, xbrl_list: TypingList[XBRL]):
        if xbrl_list is None:
            self._xbrl_list = xbrl_list
            return
        if not isinstance(xbrl_list, list):
            xbrl_list = [xbrl_list]
        if any(not isinstance(item, XBRL) for item in xbrl_list):
            raise ValueError(f"'xbrl_list' needs to be a list of XBRL")
        else:
            self._xbrl_list = xbrl_list

    @property
    def accounting_items(self):
        return self._accounting_items

    @accounting_items.setter
    def accounting_items(self, accounting_items: Union[AccountingItem, TypingList[AccountingItem]]):
        if accounting_items is None:
            self._accounting_items = accounting_items
            return
        if not isinstance(accounting_items, list):
            accounting_items = [accounting_items]
        if any(not isinstance(item, AccountingItem) for item in accounting_items):
            raise ValueError(
                f"'accounting_items' needs to be of type {AccountingItem.__name__} or a list of {AccountingItem.__name__}")
        else:
            self._accounting_items = accounting_items

    def __repr__(self) -> str:
        # Handle xbrl_list representation
        xbrl_repr = "None"
        if self.xbrl_list is not None:
            xbrl_repr = f"list[{len(self.xbrl_list)} XBRL objects]"

        # Handle accounting_item representation
        accounting_repr = "None"
        if self.accounting_items is not None:
            if isinstance(self.accounting_items, list):
                accounting_repr = f"list[{len(self.accounting_items)} AccountingItem objects]"
            else:
                accounting_repr = "1 AccountingItem object"

        return (f"{self.__class__.__name__}("
                f"xbrl_list={xbrl_repr}, "
                f"accounting_items={accounting_repr})")

"""accounting_items_config.py"""

import re
import pandas as pd
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationError
from typing import Optional, List, Dict, Literal, Union, Pattern, Unpack, TypedDict
from tabulate import tabulate
import logging

# logger
formatter = logging.Formatter('%(asctime)s : %(module)s : %(funcName)s : %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)  # Set level specifically for this logger


class ItemType(str, Enum):
    INSTANT = "instant"  # Point-in-time measurement (balance sheet items)
    DURATION = "duration"  # Over-a-period measurement (e.g. income statement items)


class StatementType(str, Enum):
    CASHFLOW = 'cashflow_statement'
    BALANCE = 'balance_sheet'
    INCOME = 'income_statement'


class MatchStrategy(str, Enum):
    CONCEPT_ONLY = "concept_only"
    LABEL_ONLY = "label_only"
    UNION = "union"  # Match EITHER concept OR label
    INTERSECTION = "intersection"  # Match BOTH concept AND label


class AccountingItem(BaseModel):
    """
    Enhanced class for accounting item configuration with better documentation
    and more comprehensive fields.
    """
    # Core identification
    name: str = Field(..., description="Human-readable name of the accounting item")
    item_type: ItemType = Field(..., description="Whether this is an instant or period measurement")
    statement: Optional[Union[Literal['income_statement', 'balance_sheet', 'cashflow_statement'], StatementType]] \
        = Field(
        ...,
        description="Which financial statement this item belongs to"
    )
    yahoo_name: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Yahoo accounting item names that can be used to match SEC concepts with data for the available "
                    "quarterly data from Yahoo Finance"
    )

    # Matching configuration and filtering
    match_strategy: Union[Literal["concept_only", "label_only", "union", "intersection"], MatchStrategy] = Field(
        default=MatchStrategy.UNION,
        description="How to combine concept and label matching"
    )
    concept_patterns: List[Pattern] = Field(
        default_factory=list,
        description="Regex patterns for XBRL concept matching"
    )
    label_patterns: List[Pattern] = Field(
        default_factory=list,
        description="Regex patterns for human-readable label matching"
    )
    allow_non_statement_data: bool = Field(
        default=False,
        description="Whether data should be filtered first on statement type or data can be included from other places "
                    "like notes"
    )
    allow_dimension_data: bool = Field(
        default=False,
        description="Whether data can be from a business segment or product line"
    )

    # Additional meta data
    can_be_sum: bool = Field(
        default=False,
        description="Whether this item can be summed across segments/divisions"
    )
    always_positive: bool = Field(
        default=True,
        description="Whether negative values should be set to positive"
    )
    allow_na: bool = Field(
        default=False,
        description="Whether NA/missing values are acceptable for this item"
    )
    calculate_ttm: bool = Field(
        default=False,
        description="Whether to calculate trailing twelve months for this item"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the accounting item",
    )

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True,
        json_encoders={Pattern: lambda p: p.pattern}
    )

    # @field_validator('concept_patterns', 'label_patterns', mode='before')
    # @classmethod
    # def compile_patterns(cls, v):
    #     """A Pydantic validator that automatically converts string patterns to compiled regex patterns
    #     @field_validator tells Pydantic this method validates specific fields ('concept_patterns' and 'label_patterns')
    #     mode='before' means it runs before other validation
    #     """
    #     if isinstance(v, str):
    #         return [re.compile(v, re.IGNORECASE)]
    #     if isinstance(v, list):
    #         return [re.compile(p, re.IGNORECASE) if isinstance(p, str) else p for p in v]
    #     return v

    def _matches_col_value(self, col_value: str) -> bool:
        """Check if concept or label matches any configured patterns (returns first match only)"""
        for p in self.concept_patterns:
            if p.search(col_value):
                return True
        return False

    # def matches_fact(self, *, concept: str, label: str) -> bool:
    #     """
    #     Determine if a fact matches based on configured strategy.
    #     The * forces all following parameters to be passed as keyword arguments
    #     You cannot call this method with positional arguments after the *
    #     Prevents confusion since both parameters are strings (concept and label)
    #     Args:
    #         concept: XBRL concept name
    #         label: Human-readable label
    #     """
    #     concept_match = self._matches_col_value(concept) if self.concept_patterns else False
    #     label_match = self._matches_col_value(label) if self.label_patterns else False
    #
    #     match self.match_strategy:
    #         case MatchStrategy.CONCEPT_ONLY:
    #             return concept_match
    #         case MatchStrategy.LABEL_ONLY:
    #             return label_match
    #         case MatchStrategy.UNION:
    #             return concept_match or label_match
    #         case MatchStrategy.INTERSECTION:
    #             return concept_match and label_match
    #         case _:
    #             raise ValueError(f"Unknown match strategy: {self.match_strategy}")

    @staticmethod
    def _get_first_matches(df: pd.DataFrame, column: str, patterns: List[Pattern]) -> pd.DataFrame:
        """Helper method to find first matches in column based on patterns.
        Returns ALL rows matching the FIRST matching pattern found (in patterns order)."""
        for pattern in patterns:
            # Use pattern.pattern for the string representation when needed
            matches = df[df[column].apply(lambda x: bool(pattern.search(x)))]
            if not matches.empty:
                return matches
        return pd.DataFrame(columns=df.columns)

    def filter_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter dataframe using pattern priority, returning first matches found."""
        # Validate strategy requirements
        if self.match_strategy == MatchStrategy.CONCEPT_ONLY and not self.concept_patterns:
            raise ValueError("Concept-only matching requires concept_patterns")
        if self.match_strategy == MatchStrategy.LABEL_ONLY and not self.label_patterns:
            raise ValueError("Label-only matching requires label_patterns")

        # Prepare dataframe (preserve original concept)
        df = df.copy()
        df['base_concept'] = df['concept'].str.extract(r'([^:]+)$', expand=False)

        result = pd.DataFrame(columns=df.columns)

        match self.match_strategy:
            case MatchStrategy.CONCEPT_ONLY:
                logger.debug(f"Filter with {MatchStrategy.CONCEPT_ONLY}")
                result = self._get_first_matches(df, 'base_concept', self.concept_patterns)

            case MatchStrategy.LABEL_ONLY:
                logger.debug(f"Filter with {MatchStrategy.LABEL_ONLY}")
                result = self._get_first_matches(df, 'label', self.label_patterns)

            case MatchStrategy.UNION:
                logger.debug(f"Filter with {MatchStrategy.UNION}")

                matches_list = []
                # Get all concept matches
                concept_matches = pd.DataFrame(columns=df.columns)
                if self.concept_patterns:
                    concept_matches = self._get_first_matches(df, 'base_concept', self.concept_patterns)
                if not concept_matches.empty:
                    matches_list.append(concept_matches)

                # Get all label matches (including those that might have matched concepts)
                label_matches = pd.DataFrame(columns=df.columns)
                if self.label_patterns:
                    label_matches = self._get_first_matches(df, 'label', self.label_patterns)
                if not label_matches.empty:
                    matches_list.append(label_matches)

                # Combine results (union of all matches)
                result = pd.concat(matches_list).drop_duplicates()

            case MatchStrategy.INTERSECTION:
                logger.debug(f"Filter with {MatchStrategy.INTERSECTION}")

                concept_matches = (self._get_first_matches(df, 'base_concept', self.concept_patterns)
                                   if self.concept_patterns else None)
                label_matches = (self._get_first_matches(df, 'label', self.label_patterns)
                                 if self.label_patterns else None)

                if concept_matches is not None and label_matches is not None:
                    common_idx = concept_matches.index.intersection(label_matches.index)
                    result = df.loc[common_idx] if not common_idx.empty else pd.DataFrame(columns=df.columns)

        # Cleanup and return (keeping original concept names)
        if not result.empty:
            result['concept'] = df.loc[result.index, 'concept'].copy()
        return result.drop(columns=['base_concept'], errors='ignore')

    @classmethod
    def validate_input_structure(cls, **kwargs):
        try:
            cls(**kwargs).model_dump(exclude_unset=True)
        except ValidationError as e:
            raise ValueError(f"Invalid input: {e}")

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return self.model_dump(exclude_unset=True)

    def __repr__(self):
        """Custom representation that shows all attributes"""
        return f"AccountingItem({super().__repr__()})"


def create_accounting_item(
        # Core identification (required fields)
        name: str,
        item_type: ItemType,
        statement: Union[Literal['income_statement', 'balance_sheet', 'cashflow_statement'], StatementType],

        # Optional fields with defaults matching AccountingItem
        yahoo_name: Optional[Union[str, List[str]]] = None,
        match_strategy: Union[Literal["concept_only", "label_only", "union", "intersection"], MatchStrategy] = MatchStrategy.UNION,
        concept_patterns: Union[str, List[Union[str, Pattern]]] = None,
        label_patterns: Union[str, List[Union[str, Pattern]]] = None,
        allow_non_statement_data: bool = False,
        allow_dimension_data: bool = False,
        can_be_sum: bool = False,
        always_positive: bool = True,
        allow_na: bool = False,
        calculate_ttm: bool = False,
        description: Optional[str] = None
) -> AccountingItem:
    """
    Factory function for creating AccountingItem instances with full IDE support.

    Args mirror all attributes from AccountingItem class with the same defaults.

    Example:
        create_accounting_item(
        ...     name="Revenue",
        ...     item_type=ItemType.DURATION,
        ...     statement=StatementType.INCOME,
        ...     concept_patterns=["RevenueFromContract"]
        ... )
    """
    # Handle pattern inputs (strings or lists)
    processed_concept_patterns = (
        [concept_patterns] if isinstance(concept_patterns, str)
        else concept_patterns if concept_patterns
        else []
    )

    processed_label_patterns = (
        [label_patterns] if isinstance(label_patterns, str)
        else label_patterns if label_patterns
        else []
    )

    if item_type == item_type.INSTANT:
        calculate_ttm = False

    return _create_accounting_item_after_validation(
        name=name,
        item_type=item_type,
        statement=statement,
        yahoo_name=yahoo_name,
        match_strategy=match_strategy,
        concept_patterns=processed_concept_patterns,
        label_patterns=processed_label_patterns,
        allow_non_statement_data=allow_non_statement_data,
        allow_dimension_data=allow_dimension_data,
        can_be_sum=can_be_sum,
        always_positive=always_positive,
        allow_na=allow_na,
        calculate_ttm=calculate_ttm,
        description=description
    )


def _create_accounting_item_after_validation(**kwargs):
    """
    Returns an instance of AccountingItem after inputs have been validated
    :param kwargs:
    :return:
    """
    # Validate the inputs first
    AccountingItem.validate_input_structure(**kwargs)
    logger.debug(f"Creating an accounting item for {kwargs['name']}:\n{tabulate(kwargs.items(), headers=["Key", "Value"], tablefmt="grid")}")
    return AccountingItem(**kwargs)


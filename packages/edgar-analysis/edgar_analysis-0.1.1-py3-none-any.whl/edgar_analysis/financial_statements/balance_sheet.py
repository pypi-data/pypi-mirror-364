"""balance_sheet.py"""

from edgar_analysis.financial_statements.accounting_items_config import create_accounting_item, ItemType, StatementType

STATEMENT = StatementType.BALANCE

TOTAL_ASSETS = create_accounting_item(
    name='Total Assets',
    item_type=ItemType.INSTANT,
    statement=STATEMENT,
    yahoo_name='Total Assets',
    concept_patterns=[r'^(Assets|Asset|TotalAsset|TotalAssets)$',  # Exact us-gaap:Assets or us-gaap:Asset
                      '^(?=.*total)(?=.*asset)(?!.*current).*$'],  # Incl. total and asset not current
    label_patterns=[r'^(Total Asset|Total Assets)$',  # Exact total asset or total assets
                    '^(?=.*total)(?=.*asset)(?!.*current).*$'],  # Incl. total and asset not current
    allow_non_statement_data=False,
    allow_dimension_data=False,
    can_be_sum=False,
    description="Sum of all current and non-current assets held by the company."
)
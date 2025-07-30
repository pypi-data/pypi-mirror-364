"""income_statement.py"""

from edgar_analysis.financial_statements.accounting_items_config import create_accounting_item, ItemType, StatementType


REVENUE = create_accounting_item(
    name="Revenue",
    item_type=ItemType.DURATION,
    statement=StatementType.INCOME,
    yahoo_name='Total Revenue',
    concept_patterns=[
        r'^(Revenue|Revenues|RevenueFromContractWithCustomer|'
        r'RevenueFromProductSales|RevenueFromContractWithCustomerExcludingAssessedTax)$',
        r'^(?!.*(cost|expense|other|service|good|product))(?=.*(revenue|sales)).*$'  # Broader pattern
        # ^(?!.*(cost|expense|other)) - Negative lookahead to exclude concepts containing "cost", "expense", or "other"
        # (?=.*(revenue|sales)) - Positive lookahead to require either "revenue" or "sales"
        # .*$ - Matches the rest of the string
    ],
    label_patterns=['total revenue', 'total sales'],
    can_be_sum=False,
    always_positive=True,
    allow_na=False,
    calculate_ttm=True,
    description="Total revenue from operations"
)




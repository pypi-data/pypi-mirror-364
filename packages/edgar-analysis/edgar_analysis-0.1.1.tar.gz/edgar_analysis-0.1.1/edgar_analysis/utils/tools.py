"""tools.py"""

import datetime


def last_day_of_month(any_day, month_offset=0):
    """
    Returns the last day of the month with an optional month offset.

    Args:
        any_day: A datetime.date or datetime.datetime object
        month_offset: Number of months to add (positive) or subtract (negative)

    Returns:
        A datetime.date object representing the last day of the month
    """
    # Calculate the target year and month
    year = any_day.year
    month = any_day.month

    # Apply the month offset
    month += month_offset
    # Adjust year if necessary
    while month > 12:
        month -= 12
        year += 1
    while month < 1:
        month += 12
        year -= 1

    # Create a new date for the 1st of the target month
    first_of_target_month = any_day.replace(year=year, month=month, day=1)

    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = first_of_target_month.replace(day=28) + datetime.timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - datetime.timedelta(days=next_month.day)



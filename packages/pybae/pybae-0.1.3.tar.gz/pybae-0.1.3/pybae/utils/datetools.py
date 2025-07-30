"""
Collection of utility functions datetime related.
"""

import datetime as dt


def is_datetime_from_yesterday(datetime: dt.datetime) -> bool:
    """Check if the given datetime is from yesterday.

    Args:
        datetime (datetime): The datetime to check.

    Returns:
        bool: True if the datetime is from yesterday, False otherwise.

    Raises:
        ValueError: If the datetime is not timezone-aware.

    """
    if datetime.tzinfo is None:
        raise ValueError("Datetime must be timezone-aware")

    yesterday = utc_now() - dt.timedelta(days=1)
    return dt.date() == yesterday.date()


def utc_now() -> dt.datetime:
    """Get the current UTC datetime.

    Returns:
        datetime: The current UTC datetime.

    """
    return dt.datetime.now(dt.UTC)

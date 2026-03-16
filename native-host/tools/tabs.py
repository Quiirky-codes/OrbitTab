# tabs.py - utility functions for tab handling

"""Utility functions for processing tab data in the native host.

Current functionality:
- group_by_date: Group a list of tab dictionaries by the calendar day
  extracted from the ``openedAt`` timestamp (milliseconds since epoch).
  If a tab lacks ``openedAt``, the current date is used.
"""

from datetime import datetime
from typing import List, Dict, Any


def group_by_date(tabs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group tabs by the date they were opened.

    Args:
        tabs: List of tab dictionaries. Each tab may contain an ``openedAt``
            field representing a Unix timestamp in milliseconds.

    Returns:
        A dictionary mapping a date string ``YYYY-MM-DD`` to a list of tab
        dictionaries that belong to that date.
    """
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for tab in tabs:
        ts = tab.get("openedAt")
        if isinstance(ts, (int, float)):
            # Convert milliseconds to seconds for datetime
            dt = datetime.fromtimestamp(ts / 1000)
        else:
            # Fallback to current date if timestamp missing or invalid
            dt = datetime.now()
        date_key = dt.strftime("%Y-%m-%d")
        groups.setdefault(date_key, []).append(tab)
    return groups

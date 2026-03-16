# group_summary.py - utility to create a concise summary for a group of tabs

"""Generate a short summary for a list of tabs.

For now this is a simple heuristic: it joins the titles of the tabs and limits the length.
If a more sophisticated LLM based summary is desired, this function can be expanded.
"""

from typing import List, Dict


def summarize_group(tabs: List[Dict]) -> str:
    """Return a short summary for the given list of tab dictionaries.

    Args:
        tabs: List of tab dicts, each containing at least a ``title`` key.
    Returns:
        A short string summarizing the group.
    """
    if not tabs:
        return "No tabs in this group."
    # Simple heuristic: list up to 3 titles, then indicate count
    titles = [t.get("title", "Untitled") for t in tabs]
    displayed = titles[:3]
    summary = ", ".join(displayed)
    if len(tabs) > 3:
        summary += f", and {len(tabs) - 3} more tabs"
    return summary

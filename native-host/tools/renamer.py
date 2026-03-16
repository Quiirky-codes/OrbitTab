# renamer.py - utility for smart renaming a tab

"""Smart rename a tab based on its content.

In a real implementation this would call a language model to generate a concise title.
For now we provide a simple placeholder that returns a generic title.
"""

def suggest_title(tab):
    """Return a suggested title for the given tab dict.

    Args:
        tab (dict): Tab information, may contain ``title`` and ``url``.
    Returns:
        str: Suggested new title.
    """
    # Placeholder implementation – prepend "Renamed:" to existing title if present
    original = tab.get("title", "Untitled")
    return f"Renamed: {original}"

# from tools.embedding import embed_tabs  # Not needed for date grouping
# from tools.clustering import cluster_embeddings  # No longer needed
from tools.summarizer import summarize_tabs
from tools.task_namer import name_task
from memory.sessions import save_session, get_sessions
from tools.tabs import group_by_date
from tools.group_summary import summarize_group
from tools.renamer import suggest_title

def handle_action(msg):
    action = msg.get("action")

    if action == "get_recent_sessions":
        return get_sessions(limit=msg.get("limit", 10))

    if action == "warmup":
        # embed_tabs([])  # force model load (no longer needed)
        return None

    if action == "organize_tabs":
        tabs = msg["tabs"]

        # embeddings = embed_tabs(tabs)  # embeddings not required for grouping
        summaries = summarize_tabs(tabs)

        # Group tabs by the openedAt date
        grouped = group_by_date(tabs)

        # Attach summaries to each tab based on original order
        for date_key, items in grouped.items():
            for tab in items:
                if tab in tabs:
                    idx = tabs.index(tab)
                    tab["summary"] = summaries[idx]
                else:
                    tab["summary"] = ""


        result = []

        for date_key, items in grouped.items():
            result.append({
                "name": date_key,
                "tabs": items
            })

        save_session(result)
        return result
    if action == "rename_tab":
        # Expect a tab dict with at least an id
        tab = msg.get("tab")
        if not isinstance(tab, dict):
            return {"error": "Invalid tab payload"}
        new_title = suggest_title(tab)
        return {"newTitle": new_title}

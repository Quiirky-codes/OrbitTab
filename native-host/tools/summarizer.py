import requests
import hashlib
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
SUMMARY_CACHE = {}

def _key(tab):
    content = tab.get("title", "") + tab.get("url", "")
    return hashlib.sha256(content.encode()).hexdigest()

def summarize_tabs(tabs):
    summaries = [None] * len(tabs)
    pending = []
    index_map = []

    # 1. Cache lookup
    for i, tab in enumerate(tabs):
        k = _key(tab)
        if k in SUMMARY_CACHE:
            summaries[i] = SUMMARY_CACHE[k]
        else:
            pending.append({
                "index": i,
                "title": tab.get("title", "Untitled"),
                "url": tab.get("url", "")
            })
            index_map.append(i)

    if not pending:
        return summaries

    # 2. VERY explicit, order-preserving prompt
    prompt = f"""
You are an AI assistant helping organize browser tabs.

TASK:
- Each tab is listed BELOW, one per line, in order.
- Write a clear, informative summary for EACH tab.
- Each summary MUST be 2–3 sentences long.
- Do NOT merge tabs.
- Do NOT skip any tab.
- Return VALID JSON ONLY.

FORMAT (strict):
{{
  "tabs": [
    {{ "index": 0, "summary": "..." }},
    {{ "index": 1, "summary": "..." }}
  ]
}}

TABS:
"""

    for t in pending:
        # If url is missing, just use title
        display_url = t["url"] if t["url"] else "No URL"
        prompt += f"{t['index']}. {t['title']} — {display_url}\n"

    try:
        # 3. Single LLM call
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "phi3",
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 600
                }
            },
            timeout=180
        )
        
        if response.status_code != 200:
             print(f"[Error] Ollama returned {response.status_code}")
             return summaries # Return partial/None summaries

        data = json.loads(response.json()["response"])

        # 4. Map back exactly by index
        for item in data.get("tabs", []):
            i = item.get("index")
            if i is not None and isinstance(i, int) and 0 <= i < len(summaries):
                summary = item.get("summary", "No summary provided.")
                summaries[i] = summary
                
                # Update cache
                # We need to find which tab this index corresponds to in the ORIGINAL tabs list
                # 'i' here is the index in the 'tabs' list passed to this function
                # The LLM is asked to return the SAME index we sent it. 
                # We sent t['index'] which IS 'i' from the original loop.
                if i < len(tabs):
                    SUMMARY_CACHE[_key(tabs[i])] = summary
                    
    except Exception as e:
        print(f"[Error] Summarization failed: {e}")
        # We process whatever we can, or just leave as None
        
    # Fill any still-None summaries
    for i in range(len(summaries)):
        if summaries[i] is None:
            summaries[i] = tabs[i].get("title", "Untitled")

    return summaries

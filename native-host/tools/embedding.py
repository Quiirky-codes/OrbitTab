from sentence_transformers import SentenceTransformer

_model = None

def embed_tabs(tabs):
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = [t.get("title", "") + " " + t.get("url", "") for t in tabs]
    return _model.encode(texts)

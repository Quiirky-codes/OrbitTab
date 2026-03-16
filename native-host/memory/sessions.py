import json
from pathlib import Path
from time import time
from cryptography.fernet import Fernet
import base64
import hashlib
import os

STORE = Path.home() / ".orbitab_sessions.enc"

# 🔒 Derive key from OS user
def _get_key():
    try:
        username = os.getlogin().encode()
    except OSError:
        username = b"default_user" 
    return base64.urlsafe_b64encode(hashlib.sha256(username).digest())

fernet = Fernet(_get_key())

def load_sessions():
    if not STORE.exists():
        return []

    try:
        encrypted = STORE.read_bytes()
        decrypted = fernet.decrypt(encrypted)
        data = json.loads(decrypted)

        # 🔒 Auto-expire old sessions (7 days)
        now = time()
        data = [
            s for s in data
            if now - s["created"] < 7 * 24 * 60 * 60
        ]

        return data

    except Exception:
        return []

def save_session(groups):
    data = load_sessions()

    data.append({
        "groups": groups,
        "created": time()
    })

    try:
        encrypted = fernet.encrypt(json.dumps(data).encode())
        STORE.write_bytes(encrypted)
    except Exception:
        pass

def get_sessions(limit=10):
    sessions = load_sessions()
    # Sort by created desc
    sessions.sort(key=lambda x: x["created"], reverse=True)
    return sessions[:limit]

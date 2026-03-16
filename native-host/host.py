#!/usr/bin/env python3

import os
import sys
import json
import time
from pathlib import Path

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "native_host.log"

# ---------------------------------------------------------------------
# Auto-activate venv
# ---------------------------------------------------------------------
if sys.prefix == sys.base_prefix:
    venv_python = BASE_DIR / "venv" / "bin" / "python3"
    if venv_python.exists():
        # Re-execute with venv python
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)
    else:
        # Fallback to system python but log warning
        with open(LOG_FILE, "a") as f:
            f.write("[Warning] venv not found, using system python\n")

ALLOWED_ACTIONS = {
    "organize_tabs",
    "get_sessions",
    "warmup"
}

MAX_TABS = 100
MAX_STRING_LENGTH = 500

# ---------------------------------------------------------------------
# Silence library noise (protect native messaging protocol)
# ---------------------------------------------------------------------
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

sys.stdout = sys.stderr  # Prevent protocol corruption

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
def log(msg):
    with LOG_FILE.open("a") as f:
        f.write(msg + "\n")
        f.flush()

# ---------------------------------------------------------------------
# Import Agent
# ---------------------------------------------------------------------
try:
    from agent import handle_action
except Exception as e:
    log(f"[Startup Error] {e}")
    sys.exit(1)

# ---------------------------------------------------------------------
# Native Messaging Helpers
# ---------------------------------------------------------------------
def read_message():
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len:
        return None

    msg_len = int.from_bytes(raw_len, "little")

    # 🔒 Prevent oversized payload attacks
    if msg_len > 10_000_000:
        log("[Security] Oversized message blocked")
        return None

    data = sys.stdin.buffer.read(msg_len).decode("utf-8")
    return json.loads(data)


def send_message(obj):
    encoded = json.dumps(obj).encode("utf-8")
    sys.__stdout__.buffer.write(len(encoded).to_bytes(4, "little"))
    sys.__stdout__.buffer.write(encoded)
    sys.__stdout__.buffer.flush()

# ---------------------------------------------------------------------
# Input Sanitization
# ---------------------------------------------------------------------
def sanitize_tabs(tabs):
    clean = []

    for t in tabs[:MAX_TABS]:  # 🔒 Limit number of tabs
        clean.append({
            "title": str(t.get("title", ""))[:MAX_STRING_LENGTH],
            "url": str(t.get("url", ""))[:2048],
            "domain": str(t.get("domain", ""))[:200],
            "tabId": t.get("tabId")
        })

    return clean

# ---------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------
def main():
    log("[Native Host] Started")

    while True:
        try:
            msg = read_message()

            if msg is None:
                time.sleep(0.05)
                continue

            action = msg.get("action")

            # 🔒 Validate action
            if action not in ALLOWED_ACTIONS:
                send_message({
                    "ok": False,
                    "error": "Unauthorized action"
                })
                continue

            # 🔒 Handle organize_tabs securely
            if action == "organize_tabs":
                tabs = msg.get("tabs", [])

                if not isinstance(tabs, list):
                    send_message({
                        "ok": False,
                        "error": "Invalid tabs payload"
                    })
                    continue

                safe_tabs = sanitize_tabs(tabs)
                result = handle_action({
                    "action": action,
                    "tabs": safe_tabs
                })

            else:
                # warmup / get_sessions
                result = handle_action(msg)

            send_message({
                "ok": True,
                "data": result
            })

        except Exception as e:
            log(f"[Runtime Error] {e}")
            send_message({
                "ok": False,
                "error": "Internal native host error"
            })
            time.sleep(0.1)

if __name__ == "__main__":
    main()

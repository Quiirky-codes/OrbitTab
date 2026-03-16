
import sys
import os
from pathlib import Path
import json

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from memory.sessions import save_session, get_sessions, STORE

def test_session_lifecycle():
    # 1. Backup existing sessions
    backup = None
    if STORE.exists():
        backup = STORE.read_text()
    
    try:
        # 2. Clear sessions
        if STORE.exists():
            STORE.unlink()
        
        # 3. Create dummy data
        groups = [{"name": "Test Group", "tabs": []}]
        
        # 4. Save session
        save_session(groups)
        
        # 5. Verify file exists
        assert STORE.exists()
        
        # 6. Get sessions
        sessions = get_sessions()
        assert len(sessions) == 1
        assert sessions[0]["groups"][0]["name"] == "Test Group"
        
        # 7. Add another
        groups2 = [{"name": "Test Group 2", "tabs": []}]
        save_session(groups2)
        
        sessions = get_sessions()
        assert len(sessions) == 2
        # Should be sorted most recent first
        assert sessions[0]["groups"][0]["name"] == "Test Group 2"
        
        print("✅ Session lifecycle test passed")
        
    finally:
        # 8. Restore backup
        if backup:
            STORE.write_text(backup)
        elif STORE.exists():
            STORE.unlink()

if __name__ == "__main__":
    test_session_lifecycle()

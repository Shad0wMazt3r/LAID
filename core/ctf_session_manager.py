import json
import os
import hashlib
import time
from datetime import datetime
from pathlib import Path

class CTFSessionManager:
    def __init__(self, base_dir=".laid_ctf"):
        self.base_dir = Path(base_dir)
        self.sessions_dir = self.base_dir / "sessions"
        self.cache_dir = self.base_dir / "cache"
        self.templates_dir = self.base_dir / "templates"
        self.current_session = None
        self.cache = {}

        # Ensure directories exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Load cache if exists
        self._load_cache()

    def create_session(self, ctf_name, challenge_name=None):
        """Create a new CTF session"""
        session_id = f"{ctf_name}_{challenge_name}" if challenge_name else ctf_name
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(exist_ok=True)

        # Create session files
        session_data = {
            "ctf_name": ctf_name,
            "challenge_name": challenge_name,
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "active",
            "paths_explored": [],
            "findings": [],
            "exploits_used": []
        }

        self._save_session_data(session_id, session_data)
        self.current_session = session_id

        # Create initial reasoning file
        reasoning_file = session_dir / "reasoning.md"
        if not reasoning_file.exists():
            reasoning_file.write_text(f"# CTF Session: {session_id}\n\n## Initial Analysis\n\n")

        # Create paths file
        paths_file = session_dir / "paths_taken.json"
        if not paths_file.exists():
            paths_file.write_text(json.dumps({"paths": []}, indent=2))

        # Create findings file
        findings_file = session_dir / "findings.md"
        if not findings_file.exists():
            findings_file.write_text(f"# Findings for {session_id}\n\n## Vulnerabilities Discovered\n\n")

        return session_id

    def set_current_session(self, session_id):
        """Set the current active session"""
        if (self.sessions_dir / session_id).exists():
            self.current_session = session_id
            return True
        return False

    def get_current_session(self):
        """Get current session data"""
        if not self.current_session:
            return None
        return self._load_session_data(self.current_session)

    def log_reasoning(self, reasoning_text, category="general"):
        """Log AI reasoning for current session"""
        if not self.current_session:
            return False

        session_dir = self.sessions_dir / self.current_session
        reasoning_file = session_dir / "reasoning.md"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n## {category.title()} - {timestamp}\n\n{reasoning_text}\n"

        with open(reasoning_file, "a") as f:
            f.write(log_entry)

        # Update session metadata
        self._update_session_timestamp()
        return True

    def log_path_explored(self, path_data):
        """Log an explored attack vector/path"""
        if not self.current_session:
            return False

        session_dir = self.sessions_dir / self.current_session
        paths_file = session_dir / "paths_taken.json"

        try:
            with open(paths_file, "r") as f:
                data = json.load(f)
        except:
            data = {"paths": []}

        # Add timestamp and path data
        path_entry = {
            "timestamp": datetime.now().isoformat(),
            "path": path_data.get("path", ""),
            "method": path_data.get("method", ""),
            "result": path_data.get("result", ""),
            "notes": path_data.get("notes", "")
        }

        data["paths"].append(path_entry)

        with open(paths_file, "w") as f:
            json.dump(data, f, indent=2)

        self._update_session_timestamp()
        return True

    def log_finding(self, finding_data):
        """Log a security finding"""
        if not self.current_session:
            return False

        session_dir = self.sessions_dir / self.current_session
        findings_file = session_dir / "findings.md"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        finding_entry = f"\n## Finding - {timestamp}\n\n"
        finding_entry += f"**Type:** {finding_data.get('type', 'Unknown')}\n"
        finding_entry += f"**Severity:** {finding_data.get('severity', 'Unknown')}\n"
        finding_entry += f"**Description:** {finding_data.get('description', '')}\n"
        finding_entry += f"**Location:** {finding_data.get('location', '')}\n"
        finding_entry += f"**Evidence:** {finding_data.get('evidence', '')}\n"
        finding_entry += f"**Remediation:** {finding_data.get('remediation', '')}\n\n"

        with open(findings_file, "a") as f:
            f.write(finding_entry)

        self._update_session_timestamp()
        return True

    def get_cache_key(self, input_data):
        """Generate cache key from input data"""
        if isinstance(input_data, dict):
            input_str = json.dumps(input_data, sort_keys=True)
        else:
            input_str = str(input_data)
        return hashlib.md5(input_str.encode()).hexdigest()

    def get_cached_response(self, cache_key):
        """Get cached response if exists and not expired"""
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached["timestamp"] < 3600:  # 1 hour cache
                return cached["response"]
            else:
                # Remove expired cache
                del self.cache[cache_key]
                self._save_cache()
        return None

    def cache_response(self, cache_key, response):
        """Cache a response"""
        self.cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        self._save_cache()

    def list_sessions(self):
        """List all available sessions"""
        return [d.name for d in self.sessions_dir.iterdir() if d.is_dir()]

    def get_session_summary(self, session_id=None):
        """Get summary of a session"""
        if not session_id:
            session_id = self.current_session
        if not session_id:
            return None

        session_data = self._load_session_data(session_id)
        if not session_data:
            return None

        session_dir = self.sessions_dir / session_id

        # Count paths explored
        paths_file = session_dir / "paths_taken.json"
        paths_count = 0
        if paths_file.exists():
            try:
                with open(paths_file, "r") as f:
                    data = json.load(f)
                    paths_count = len(data.get("paths", []))
            except:
                pass

        # Count findings
        findings_file = session_dir / "findings.md"
        findings_count = 0
        if findings_file.exists():
            content = findings_file.read_text()
            findings_count = content.count("## Finding")

        return {
            "session_id": session_id,
            "ctf_name": session_data.get("ctf_name"),
            "challenge_name": session_data.get("challenge_name"),
            "created_at": session_data.get("created_at"),
            "last_updated": session_data.get("last_updated"),
            "status": session_data.get("status"),
            "paths_explored": paths_count,
            "findings_count": findings_count
        }

    def _load_session_data(self, session_id):
        """Load session metadata"""
        session_dir = self.sessions_dir / session_id
        metadata_file = session_dir / "session.json"

        if metadata_file.exists():
            try:
                with open(metadata_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return None

    def _save_session_data(self, session_id, data):
        """Save session metadata"""
        session_dir = self.sessions_dir / session_id
        metadata_file = session_dir / "session.json"

        with open(metadata_file, "w") as f:
            json.dump(data, f, indent=2)

    def _update_session_timestamp(self):
        """Update last updated timestamp for current session"""
        if not self.current_session:
            return

        session_data = self._load_session_data(self.current_session)
        if session_data:
            session_data["last_updated"] = datetime.now().isoformat()
            self._save_session_data(self.current_session, session_data)

    def _load_cache(self):
        """Load cache from disk"""
        cache_file = self.cache_dir / "cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    self.cache = json.load(f)
            except:
                self.cache = {}

    def _save_cache(self):
        """Save cache to disk"""
        cache_file = self.cache_dir / "cache.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass

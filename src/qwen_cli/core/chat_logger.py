import json
import os
from datetime import datetime
from pathlib import Path

class ChatLogger:
    """Manages chat session logging with file rotation."""
    def __init__(self, history_dir: Path, title: str, max_bytes: int = 1 * 1024 * 1024):
        self.history_dir = history_dir
        self.title = title
        self.max_bytes = max_bytes
        self.log_fp = None
        self.log_path = None
        self._open_log()

    def _next_index(self, start_at: int = 1) -> int:
        safe_title = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in self.title).strip("-") or "session"
        date_str = datetime.now().strftime("%Y-%m-%d")
        existing = list(self.history_dir.glob(f"{safe_title}-{date_str}-*.jsonl"))
        max_i = 0
        for p in existing:
            try:
                i_str = p.stem.split("-")[-1]
                i_val = int(i_str)
                if i_val > max_i:
                    max_i = i_val
            except (ValueError, IndexError):
                continue
        return max(max_i, start_at)

    def _open_log(self, index: int = 1):
        safe_title = "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in self.title).strip("-") or "session"
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.log_path = self.history_dir / f"{safe_title}-{date_str}-{index}.jsonl"
        self.log_fp = self.log_path.open("a", encoding="utf-8")
        print(f"📝 Logging to: {self.log_path}")

    def log_message(self, role: str, content: str):
        if not self.log_fp:
            return
        try:
            # Check for file size before writing and rotate if necessary
            if self.log_path and self.log_path.stat().st_size >= self.max_bytes:
                self.close()
                current_i = int(self.log_path.stem.split("-")[-1])
                self._open_log(current_i + 1)
                print(f"📝 Rolled log to: {self.log_path}")

            message = {"role": role, "content": content}
            self.log_fp.write(json.dumps(message) + "\n")
            self.log_fp.flush()
        except Exception:
            # In case of any logging error, close the file handle to prevent issues
            self.close()

    def close(self):
        if self.log_fp:
            try:
                self.log_fp.close()
            except Exception:
                pass
            self.log_fp = None

    def __del__(self):
        self.close()